"""
TRIDENT Triage Decision Engine

Implements the full 3C framework (Confidence × Content × Concern) for emergency call
prioritization, as specified in PRD Section 5.

This version includes the NLP Content layer for complete 3D decision matrix.

Priority Queues (from PRD Table 3):
- Q1-IMMEDIATE: Critical, needs dispatcher attention now
- Q2-ELEVATED: High priority, review soon
- Q3-MONITOR: Elevated concern but clear communication
- Q4-STANDARD: Medium priority, process normally
- Q5-REVIEW: Low confidence, needs verification
- Q5-ROUTINE: Standard logging, no urgency

Key Insight (from PRD):
"ASR failure is a feature" - Low confidence + high distress indicates
Caribbean creole under emotional stress = highest priority scenario.
"""

from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TriageEngine:
    """
    Implements emergency call triage decision logic.

    Uses ASR confidence, NLP content indicators, and bio-acoustic distress
    to route calls to appropriate priority queues via 3D decision matrix.
    """

    # Thresholds from PRD
    CONFIDENCE_THRESHOLD = 0.7  # Below this = low confidence
    DISTRESS_THRESHOLD = 0.5    # Above this = high distress (Concern)
    CONTENT_THRESHOLD = 0.4     # Above this = high content urgency (lowered to catch fires)

    def __init__(self):
        """Initialize triage engine with thresholds."""
        self.confidence_threshold = self.CONFIDENCE_THRESHOLD
        self.distress_threshold = self.DISTRESS_THRESHOLD
        self.content_threshold = self.CONTENT_THRESHOLD

    def prioritize_call(
        self,
        confidence: float,
        distress_score: float,
        content_score: float = 0.0
    ) -> Dict[str, any]:
        """
        Determine call priority queue using 3D decision matrix.

        Full 3D Decision Matrix (Confidence × Content × Concern):
        From PRD Table 3 - All 8 combinations of the three binary factors.

        Args:
            confidence: ASR confidence score (0-1)
            distress_score: Bio-acoustic distress score (0-1) [Concern]
            content_score: NLP content indicator (0-1)

        Returns:
            Dictionary containing:
                - queue: Priority queue assignment
                - priority_level: Numeric priority (1=highest)
                - flag_audio_review: Whether to flag for human audio review
                - reasoning: Explanation of routing decision
        """
        # Classify each dimension as High/Low
        high_confidence = confidence >= self.confidence_threshold
        high_content = content_score > self.content_threshold
        high_concern = distress_score > self.distress_threshold

        # 3D Decision Matrix - PRD Table 3
        # Format: (Confidence, Content, Concern) → Queue

        # CASE 1: Low Confidence + Low Content + High Concern
        # → Q1-IMMEDIATE (HERO SCENARIO)
        # Caribbean creole under stress, unclear content but high distress
        if not high_confidence and not high_content and high_concern:
            return {
                "queue": "Q1-IMMEDIATE",
                "priority_level": 1,
                "flag_audio_review": True,
                "reasoning": "HERO SCENARIO: Low confidence + high distress with unclear content. "
                            "Likely Caribbean creole speaker under extreme stress. "
                            "IMMEDIATE audio review required - life threat probable."
            }

        # CASE 2: Low Confidence + High Content + Low Concern
        # → Q2-ELEVATED
        # Poor transcription but serious incident reported calmly
        elif not high_confidence and high_content and not high_concern:
            return {
                "queue": "Q2-ELEVATED",
                "priority_level": 2,
                "flag_audio_review": True,
                "reasoning": "Serious incident reported but transcription unclear. "
                            "Calm delivery suggests controlled situation. "
                            "Review audio to verify content urgency."
            }

        # CASE 3: Low Confidence + High Content + High Concern
        # → Q1-IMMEDIATE
        # Poor transcription + serious incident + high distress
        elif not high_confidence and high_content and high_concern:
            return {
                "queue": "Q1-IMMEDIATE",
                "priority_level": 1,
                "flag_audio_review": True,
                "reasoning": "Critical situation: High content urgency + high distress with unclear transcription. "
                            "Multiple emergency indicators present. IMMEDIATE response required."
            }

        # CASE 4: High Confidence + Low Content + High Concern
        # → Q3-MONITOR
        # Clear speech, no semantic urgency, but elevated stress
        elif high_confidence and not high_content and high_concern:
            return {
                "queue": "Q3-MONITOR",
                "priority_level": 3,
                "flag_audio_review": False,
                "reasoning": "Clear transcription with elevated distress but low content urgency. "
                            "May be emotional caller reporting non-critical incident. Monitor situation."
            }

        # CASE 5: High Confidence + High Content + Low Concern
        # → Q2-ELEVATED
        # Professional reporting serious incident calmly
        elif high_confidence and high_content and not high_concern:
            return {
                "queue": "Q2-ELEVATED",
                "priority_level": 2,
                "flag_audio_review": False,
                "reasoning": "Serious incident reported clearly and calmly. "
                            "Professional or controlled caller. Elevated priority for content urgency."
            }

        # CASE 6: High Confidence + High Content + High Concern
        # → Q1-IMMEDIATE
        # Clear report of critical incident with distress
        elif high_confidence and high_content and high_concern:
            return {
                "queue": "Q1-IMMEDIATE",
                "priority_level": 1,
                "flag_audio_review": False,
                "reasoning": "Maximum urgency: Clear critical incident with high distress. "
                            "All three indicators elevated. IMMEDIATE dispatch required."
            }

        # CASE 7: Low Confidence + Low Content + Low Concern
        # → Q5-REVIEW
        # Unclear transcription, no urgency indicators
        elif not high_confidence and not high_content and not high_concern:
            return {
                "queue": "Q5-REVIEW",
                "priority_level": 5,
                "flag_audio_review": True,
                "reasoning": "Low confidence transcription with no urgency indicators. "
                            "Review audio when available to verify content."
            }

        # CASE 8: High Confidence + Low Content + Low Concern
        # → Q5-ROUTINE
        # Standard infrastructure report, auto-log
        else:  # high_confidence and not high_content and not high_concern
            return {
                "queue": "Q5-ROUTINE",
                "priority_level": 5,
                "flag_audio_review": False,
                "reasoning": "Clear communication with low urgency content and calm delivery. "
                            "Standard infrastructure report for routine logging."
            }

    def generate_dispatcher_guidance(
        self,
        confidence: float,
        distress_score: float,
        transcript: str,
        content_score: float = 0.0
    ) -> Dict[str, any]:
        """
        Generate comprehensive dispatcher guidance.

        Args:
            confidence: ASR confidence score
            distress_score: Bio-acoustic distress score
            transcript: Transcribed text
            content_score: NLP content indicator score

        Returns:
            Dictionary with triage decision and dispatcher instructions
        """
        triage = self.prioritize_call(confidence, distress_score, content_score)

        # Add dispatcher-specific guidance based on priority
        if triage["queue"] == "Q1-IMMEDIATE":
            triage["dispatcher_action"] = (
                "🚨 IMMEDIATE ATTENTION REQUIRED: "
                "Listen to audio immediately. Critical emergency indicators detected. "
                "Caller may be using heavy Patois or speaking under extreme stress. "
                "Prepare for immediate dispatch and potential multi-unit response."
            )
            triage["escalation_required"] = True

        elif triage["queue"] == "Q2-ELEVATED":
            triage["dispatcher_action"] = (
                "⚠️ HIGH PRIORITY: "
                "Serious incident reported. Review transcript and extracted entities for dispatch. "
                "Content indicators suggest significant emergency requiring prompt response. "
                "Verify location and hazard type, dispatch appropriate units."
            )
            triage["escalation_required"] = False

        elif triage["queue"] == "Q3-MONITOR":
            triage["dispatcher_action"] = (
                "👁️ MONITOR SITUATION: "
                "Caller shows stress indicators but communication is clear. "
                "Content does not indicate immediate life threat. "
                "Monitor for escalation, assess dispatch priority based on available resources."
            )
            triage["escalation_required"] = False

        elif triage["queue"] == "Q5-REVIEW":
            triage["dispatcher_action"] = (
                "📋 REVIEW WHEN AVAILABLE: "
                "Audio review recommended due to low transcription confidence. "
                "No immediate distress or content urgency indicators. "
                "Verify content when time permits, may require callback."
            )
            triage["escalation_required"] = False

        else:  # Q5-ROUTINE
            triage["dispatcher_action"] = (
                "�� ROUTINE LOGGING: "
                "Standard infrastructure report with clear communication. "
                "Log details and create dispatch order according to standard procedures. "
                "No elevated priority required."
            )
            triage["escalation_required"] = False

        return triage


def triage_call(
    confidence: float,
    distress_score: float,
    transcript: str = ""
) -> Dict[str, any]:
    """
    Convenience function for call triage.

    Args:
        confidence: ASR confidence score (0-1)
        distress_score: Bio-acoustic distress score (0-1)
        transcript: Optional transcript text

    Returns:
        Triage decision dictionary
    """
    engine = TriageEngine()
    return engine.generate_dispatcher_guidance(confidence, distress_score, transcript)


if __name__ == "__main__":
    # Test triage scenarios from PRD
    print("\n" + "=" * 60)
    print("TRIDENT TRIAGE ENGINE - TEST SCENARIOS")
    print("=" * 60)

    scenarios = [
        {
            "name": "Calm Infrastructure Report",
            "confidence": 0.92,
            "distress": 0.15,
            "description": "Clear Caribbean English, calm delivery"
        },
        {
            "name": "HERO SCENARIO - Distressed Basilect",
            "confidence": 0.31,
            "distress": 0.94,
            "description": "Heavy Patois, high stress, life-threatening"
        },
        {
            "name": "Stressed Professional",
            "confidence": 0.88,
            "distress": 0.68,
            "description": "Clear speech but elevated stress"
        },
        {
            "name": "Unclear Non-Urgent",
            "confidence": 0.45,
            "distress": 0.22,
            "description": "Poor connection, low urgency"
        }
    ]

    for scenario in scenarios:
        print(f"\n{'-' * 60}")
        print(f"Scenario: {scenario['name']}")
        print(f"  {scenario['description']}")
        print(f"  Confidence: {scenario['confidence']:.2f}")
        print(f"  Distress:   {scenario['distress']:.2f}")

        result = triage_call(
            scenario['confidence'],
            scenario['distress'],
            scenario['description']
        )

        print(f"\n  QUEUE: {result['queue']}")
        print(f"  Priority Level: {result['priority_level']}")
        print(f"  Audio Review: {'YES' if result['flag_audio_review'] else 'NO'}")
        print(f"  Escalate: {'YES' if result['escalation_required'] else 'NO'}")
        print(f"\n  Reasoning: {result['reasoning']}")
        print(f"\n  Dispatcher Action:")
        print(f"  {result['dispatcher_action']}")

    print("\n" + "=" * 60)
