"""
TRIDENT Triage Decision Engine

Implements the 3C framework (Confidence × Content × Concern) for emergency call
prioritization, as specified in PRD Section 5.

For this PoC, we implement a simplified 2D matrix (Confidence × Concern) since
the NLP Content layer is not yet implemented.

Priority Queues (from PRD Table 3):
- Q1-IMMEDIATE: Critical, needs dispatcher attention now
- Q2-ELEVATED: High priority, review soon
- Q3-MONITOR: Elevated concern but clear communication
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

    Uses ASR confidence and bio-acoustic distress to route calls to
    appropriate priority queues.
    """

    # Thresholds from PRD
    CONFIDENCE_THRESHOLD = 0.7  # Below this = low confidence
    DISTRESS_THRESHOLD = 0.5    # Above this = high distress

    def __init__(self):
        """Initialize triage engine with thresholds."""
        self.confidence_threshold = self.CONFIDENCE_THRESHOLD
        self.distress_threshold = self.DISTRESS_THRESHOLD

    def prioritize_call(
        self,
        confidence: float,
        distress_score: float,
        content_score: float = 0.0  # Reserved for future NLP layer
    ) -> Dict[str, any]:
        """
        Determine call priority queue based on confidence and distress.

        Simplified 2D Decision Matrix (Confidence × Concern):

        +------------------+------------------+------------------+
        |                  |  Low Distress    |  High Distress   |
        |                  |    (≤0.5)        |    (>0.5)        |
        +------------------+------------------+------------------+
        | High Confidence  |  Q5-ROUTINE      |  Q3-MONITOR      |
        |   (≥0.7)         |  Auto-log        |  Elevated watch  |
        +------------------+------------------+------------------+
        | Low Confidence   |  Q5-REVIEW       |  Q1-IMMEDIATE    |
        |   (<0.7)         |  Verify          |  PRIORITY #1     |
        +------------------+------------------+------------------+

        Args:
            confidence: ASR confidence score (0-1)
            distress_score: Bio-acoustic distress score (0-1)
            content_score: NLP content indicator (0-1) - not yet implemented

        Returns:
            Dictionary containing:
                - queue: Priority queue assignment
                - priority_level: Numeric priority (1=highest)
                - flag_audio_review: Whether to flag for human audio review
                - reasoning: Explanation of routing decision
        """
        high_confidence = confidence >= self.confidence_threshold
        high_distress = distress_score > self.distress_threshold

        # Q1-IMMEDIATE: Low confidence + high distress
        # This is the HERO scenario - Caribbean creole under stress
        if not high_confidence and high_distress:
            return {
                "queue": "Q1-IMMEDIATE",
                "priority_level": 1,
                "flag_audio_review": True,
                "reasoning": "Low ASR confidence + high bio-acoustic distress indicates "
                            "potential life-threatening situation with communication barriers. "
                            "IMMEDIATE dispatcher review required."
            }

        # Q3-MONITOR: High confidence + high distress
        # Clear communication but elevated distress - monitor situation
        elif high_confidence and high_distress:
            return {
                "queue": "Q3-MONITOR",
                "priority_level": 3,
                "flag_audio_review": False,
                "reasoning": "Clear transcription with elevated bio-acoustic distress. "
                            "Situation requires monitoring but communication is functional."
            }

        # Q5-REVIEW: Low confidence + low distress
        # Unclear communication but no urgency - verify later
        elif not high_confidence and not high_distress:
            return {
                "queue": "Q5-REVIEW",
                "priority_level": 5,
                "flag_audio_review": True,
                "reasoning": "Low ASR confidence requires verification. "
                            "No immediate distress indicators. Review audio when available."
            }

        # Q5-ROUTINE: High confidence + low distress
        # Standard infrastructure report - auto-log
        else:
            return {
                "queue": "Q5-ROUTINE",
                "priority_level": 5,
                "flag_audio_review": False,
                "reasoning": "Clear communication, calm delivery. "
                            "Standard infrastructure report for logging."
            }

    def generate_dispatcher_guidance(
        self,
        confidence: float,
        distress_score: float,
        transcript: str
    ) -> Dict[str, any]:
        """
        Generate comprehensive dispatcher guidance.

        Args:
            confidence: ASR confidence score
            distress_score: Bio-acoustic distress score
            transcript: Transcribed text

        Returns:
            Dictionary with triage decision and dispatcher instructions
        """
        triage = self.prioritize_call(confidence, distress_score)

        # Add dispatcher-specific guidance based on priority
        if triage["queue"] == "Q1-IMMEDIATE":
            triage["dispatcher_action"] = (
                "IMMEDIATE ATTENTION REQUIRED: "
                "Listen to audio immediately. High distress detected with poor transcription quality. "
                "Caller may be using heavy Patois or speaking under extreme stress. "
                "Prepare for potential evacuation or emergency response."
            )
            triage["escalation_required"] = True

        elif triage["queue"] == "Q3-MONITOR":
            triage["dispatcher_action"] = (
                "ELEVATED PRIORITY: "
                "Review transcript for dispatch requirements. Caller shows stress indicators "
                "but communication is clear. Assess situation urgency from content."
            )
            triage["escalation_required"] = False

        elif triage["queue"] == "Q5-REVIEW":
            triage["dispatcher_action"] = (
                "REVIEW WHEN AVAILABLE: "
                "Audio review recommended due to low transcription confidence. "
                "No immediate distress indicators. Verify content when time permits."
            )
            triage["escalation_required"] = False

        else:  # Q5-ROUTINE
            triage["dispatcher_action"] = (
                "ROUTINE LOGGING: "
                "Standard infrastructure report. Log details and create dispatch order "
                "according to standard procedures."
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
