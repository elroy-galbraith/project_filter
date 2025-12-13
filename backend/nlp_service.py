"""
TRIDENT Layer 2: NLP Entity Extraction Service
Uses Llama 3 via Ollama for structured entity extraction from emergency call transcripts.

Based on TRIDENT PRD Section 4.3
"""

import json
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class NLPService:
    """
    Extracts structured entities from emergency call transcripts using Llama 3.

    Entity Schema (from PRD Section 4.3.1):
    - location: Street addresses, landmarks, geographic references
    - mechanism_hazard: Type of emergency (fire, flood, medical, violence, etc.)
    - clinical_indicators: Breathing, consciousness, bleeding, mobility status
    - scale: Number of persons affected, vulnerable population flags
    """

    def __init__(self, model_name: str = "llama3.2:latest", ollama_url: str = "http://localhost:11434"):
        """
        Initialize NLP service with Ollama backend.

        Args:
            model_name: Ollama model to use (default: llama3.2:latest)
            ollama_url: Ollama API endpoint
        """
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.api_endpoint = f"{ollama_url}/api/generate"

        logger.info(f"Initialized NLP service with model: {model_name}")

    def extract_entities(self, transcript: str, confidence: float) -> Dict[str, Any]:
        """
        Extract structured entities from emergency call transcript.

        Args:
            transcript: ASR-generated transcript text
            confidence: ASR confidence score (0-1)

        Returns:
            Dictionary containing extracted entities and content score
        """
        try:
            # Build prompt with confidence-aware instructions
            prompt = self._build_extraction_prompt(transcript, confidence)

            # Call Ollama API
            response = self._call_ollama(prompt)

            # Parse JSON response
            entities = self._parse_response(response)

            # Compute content indicator score
            content_score = self._compute_content_score(entities)

            return {
                "entities": entities,
                "content_score": content_score,
                "raw_response": response
            }

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {
                "entities": self._get_empty_entities(),
                "content_score": 0.0,
                "error": str(e)
            }

    def _build_extraction_prompt(self, transcript: str, confidence: float) -> str:
        """
        Build Llama 3 prompt for entity extraction.
        Includes confidence-aware handling for low-quality transcripts.
        """

        # Low-confidence handling (PRD Section 4.3.2)
        confidence_note = ""
        if confidence < 0.7:
            confidence_note = """
IMPORTANT: This transcript has low confidence (possible accent/dialect interference).
Focus on extracting clear entities even if grammar is imperfect.
Look for keywords rather than perfect sentence structure.
"""

        prompt = f"""You are an emergency call analysis assistant for Caribbean emergency services.

Extract structured information from the following emergency call transcript.

{confidence_note}

TRANSCRIPT:
"{transcript}"

Extract the following entities in JSON format:

{{
  "location": {{
    "address": "street address if mentioned, otherwise null",
    "landmark": "recognizable landmark if mentioned, otherwise null",
    "geographic_ref": "area/district/parish if mentioned, otherwise null"
  }},
  "mechanism_hazard": "fire | flood | medical | violence | traffic | infrastructure | other",
  "clinical_indicators": {{
    "breathing": "normal | impaired | not_breathing | unknown",
    "consciousness": "alert | altered | unresponsive | unknown",
    "bleeding": "none | minor | heavy | unknown",
    "mobility": "walking | impaired | immobile | unknown"
  }},
  "scale": {{
    "persons_affected": <integer or 0 if unknown>,
    "vulnerable_population": <true if children/elderly/disabled mentioned, false otherwise>,
    "escalating": <true if situation described as worsening, false otherwise>
  }},
  "urgency_keywords": [<list of urgent words like "help", "emergency", "dying", etc.>]
}}

Return ONLY the JSON object, no additional text.
"""
        return prompt

    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API for text generation.

        Args:
            prompt: Formatted prompt for Llama 3

        Returns:
            Generated text response
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,  # Low temperature for structured output
                "format": "json"     # Request JSON formatting
            }

            logger.info(f"Calling Ollama API at {self.api_endpoint}")
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=30  # 30 second timeout
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}")
            raise

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Llama 3 JSON response into structured entities.

        Args:
            response: Raw text response from Llama 3

        Returns:
            Parsed entity dictionary
        """
        try:
            # Remove any markdown formatting if present
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned.replace("```json", "").replace("```", "").strip()

            entities = json.loads(cleaned)

            # Validate required fields
            required_fields = ["location", "mechanism_hazard", "clinical_indicators", "scale"]
            for field in required_fields:
                if field not in entities:
                    logger.warning(f"Missing required field: {field}")
                    entities[field] = self._get_empty_entities()[field]

            return entities

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response}")
            return self._get_empty_entities()

    def _get_empty_entities(self) -> Dict[str, Any]:
        """Return empty entity structure for error cases."""
        return {
            "location": {
                "address": None,
                "landmark": None,
                "geographic_ref": None
            },
            "mechanism_hazard": "other",
            "clinical_indicators": {
                "breathing": "unknown",
                "consciousness": "unknown",
                "bleeding": "unknown",
                "mobility": "unknown"
            },
            "scale": {
                "persons_affected": 0,
                "vulnerable_population": False,
                "escalating": False
            },
            "urgency_keywords": []
        }

    def _compute_content_score(self, entities: Dict[str, Any]) -> float:
        """
        Compute Content Indicator Score (Sc) based on extracted entities.

        Formula (from PRD Section 4.3.4):
        Sc = min(100, S_hazard + S_threat + S_vuln + S_scale)

        Returns:
            Content score normalized to 0-1 range
        """
        score = 0.0
        score_breakdown = {}

        # 1. Hazard Score (S_hazard)
        # Increased fire weight to ensure structure fires escalate properly
        hazard_weights = {
            "violence": 35,  # Increased - immediate life threat
            "fire": 35,      # Increased - structure fires are life-threatening
            "medical": 25,   # Increased - medical emergencies need urgency
            "flood": 20,
            "traffic": 15,
            "infrastructure": 10,
            "other": 5
        }
        hazard = entities.get("mechanism_hazard", "other")
        hazard_score = hazard_weights.get(hazard, 5)
        score += hazard_score
        score_breakdown["hazard"] = hazard_score

        # 2. Life Threat Score (S_threat)
        clinical = entities.get("clinical_indicators", {})
        threat_score = 0

        # Breathing status
        breathing = clinical.get("breathing", "unknown")
        if breathing == "not_breathing":
            threat_score += 30  # Imminent threat
        elif breathing == "impaired":
            threat_score += 15  # Potential threat

        # Consciousness status
        consciousness = clinical.get("consciousness", "unknown")
        if consciousness == "unresponsive":
            threat_score += 30  # Imminent threat
        elif consciousness == "altered":
            threat_score += 15  # Potential threat

        # Bleeding status
        bleeding = clinical.get("bleeding", "unknown")
        if bleeding == "heavy":
            threat_score += 30  # Imminent threat
        elif bleeding == "minor":
            threat_score += 5

        score += threat_score
        score_breakdown["threat"] = threat_score

        # 3. Vulnerable Population Score (S_vuln)
        scale = entities.get("scale", {})
        vuln_score = 15 if scale.get("vulnerable_population", False) else 0
        score += vuln_score
        score_breakdown["vulnerable"] = vuln_score

        # 4. Scale Score (S_scale)
        scale_score = 0
        persons = scale.get("persons_affected", 0)
        if persons is not None and persons > 0:
            scale_score += min(20, persons * 5)  # Cap at +20

        if scale.get("escalating", False):
            scale_score += 10

        score += scale_score
        score_breakdown["scale"] = scale_score

        # 5. Location Score (bonus for specific location)
        location = entities.get("location", {})
        location_score = 5 if (location.get("address") or location.get("landmark")) else 0
        score += location_score
        score_breakdown["location"] = location_score

        # 6. Urgency Keywords Score (NEW)
        # Add bonus for explicit urgency language
        urgency_keywords = entities.get("urgency_keywords", [])
        urgency_score = 0
        if urgency_keywords and len(urgency_keywords) > 0:
            # +5 points per urgency keyword, capped at +15
            urgency_score = min(15, len(urgency_keywords) * 5)
        score += urgency_score
        score_breakdown["urgency_keywords"] = urgency_score

        # Normalize to 0-1 range (cap at 100, then divide)
        normalized_score = min(100, score) / 100.0

        logger.info(f"Content score computed: {normalized_score:.2f} (raw: {score})")
        logger.info(f"Score breakdown: {score_breakdown}")
        logger.info(f"Extracted entities: hazard={hazard}, escalating={scale.get('escalating', False)}, "
                   f"persons={persons}, clinical={clinical}")
        return normalized_score


def test_nlp_service():
    """Quick test of NLP service."""
    service = NLPService()

    test_cases = [
        {
            "transcript": "There's a fire at 123 Main Street! Multiple people trapped, I can hear them screaming!",
            "confidence": 0.9
        },
        {
            "transcript": "Man down by di market, him nah breathe good, blood everywhere",
            "confidence": 0.5
        },
        {
            "transcript": "Traffic accident on Highway 1, two vehicles, one person not moving",
            "confidence": 0.8
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}")
        print(f"Transcript: {test['transcript']}")
        print(f"Confidence: {test['confidence']}")

        result = service.extract_entities(test['transcript'], test['confidence'])

        print(f"\nExtracted Entities:")
        print(json.dumps(result['entities'], indent=2))
        print(f"\nContent Score: {result['content_score']:.2f}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_nlp_service()
