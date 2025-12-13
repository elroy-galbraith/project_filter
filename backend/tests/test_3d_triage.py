"""
Test suite for 3D Triage Decision Matrix

Tests all 8 combinations of the Confidence × Content × Concern matrix
from PRD Table 3.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from triage_engine import TriageEngine
import json


def test_3d_triage_matrix():
    """
    Test all 8 cases from PRD Table 3

    3D Matrix: (Confidence, Content, Concern) → Queue

    Truth table:
    | Confidence | Content | Concern | Expected Queue |
    |------------|---------|---------|----------------|
    | Low        | Low     | High    | Q1-IMMEDIATE   |
    | Low        | High    | Low     | Q2-ELEVATED    |
    | Low        | High    | High    | Q1-IMMEDIATE   |
    | High       | Low     | High    | Q3-MONITOR     |
    | High       | High    | Low     | Q2-ELEVATED    |
    | High       | High    | High    | Q1-IMMEDIATE   |
    | Low        | Low     | Low     | Q5-REVIEW      |
    | High       | Low     | Low     | Q5-ROUTINE     |
    """

    engine = TriageEngine()

    # Test cases: (confidence, content, distress, expected_queue, scenario)
    test_cases = [
        # CASE 1: Low Conf + Low Content + High Concern → Q1-IMMEDIATE (HERO)
        {
            "confidence": 0.4,
            "content": 0.3,
            "distress": 0.8,
            "expected_queue": "Q1-IMMEDIATE",
            "expected_priority": 1,
            "scenario": "HERO SCENARIO: Caribbean creole under extreme stress",
            "should_flag_audio": True
        },

        # CASE 2: Low Conf + High Content + Low Concern → Q2-ELEVATED
        {
            "confidence": 0.5,
            "content": 0.7,
            "distress": 0.3,
            "expected_queue": "Q2-ELEVATED",
            "expected_priority": 2,
            "scenario": "Serious incident but unclear transcription, calm delivery",
            "should_flag_audio": True
        },

        # CASE 3: Low Conf + High Content + High Concern → Q1-IMMEDIATE
        {
            "confidence": 0.4,
            "content": 0.8,
            "distress": 0.9,
            "expected_queue": "Q1-IMMEDIATE",
            "expected_priority": 1,
            "scenario": "Critical: High urgency + high distress + poor transcription",
            "should_flag_audio": True
        },

        # CASE 4: High Conf + Low Content + High Concern → Q3-MONITOR
        {
            "confidence": 0.9,
            "content": 0.2,
            "distress": 0.7,
            "expected_queue": "Q3-MONITOR",
            "expected_priority": 3,
            "scenario": "Clear speech, elevated stress, but low content urgency",
            "should_flag_audio": False
        },

        # CASE 5: High Conf + High Content + Low Concern → Q2-ELEVATED
        {
            "confidence": 0.85,
            "content": 0.75,
            "distress": 0.25,
            "expected_queue": "Q2-ELEVATED",
            "expected_priority": 2,
            "scenario": "Professional reporting serious incident calmly",
            "should_flag_audio": False
        },

        # CASE 6: High Conf + High Content + High Concern → Q1-IMMEDIATE
        {
            "confidence": 0.92,
            "content": 0.85,
            "distress": 0.88,
            "expected_queue": "Q1-IMMEDIATE",
            "expected_priority": 1,
            "scenario": "Maximum urgency: All three indicators elevated",
            "should_flag_audio": False
        },

        # CASE 7: Low Conf + Low Content + Low Concern → Q5-REVIEW
        {
            "confidence": 0.45,
            "content": 0.15,
            "distress": 0.22,
            "expected_queue": "Q5-REVIEW",
            "expected_priority": 5,
            "scenario": "Unclear transcription, no urgency indicators",
            "should_flag_audio": True
        },

        # CASE 8: High Conf + Low Content + Low Concern → Q5-ROUTINE
        {
            "confidence": 0.93,
            "content": 0.18,
            "distress": 0.12,
            "expected_queue": "Q5-ROUTINE",
            "expected_priority": 5,
            "scenario": "Standard infrastructure report, auto-log",
            "should_flag_audio": False
        }
    ]

    print("\n" + "=" * 80)
    print("3D TRIAGE MATRIX TEST - ALL 8 CASES")
    print("=" * 80)

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST CASE {i}: {test['scenario']}")
        print(f"{'─' * 80}")
        print(f"Input:")
        print(f"  Confidence: {test['confidence']:.2f} ({'High' if test['confidence'] >= 0.7 else 'Low'})")
        print(f"  Content:    {test['content']:.2f} ({'High' if test['content'] > 0.5 else 'Low'})")
        print(f"  Distress:   {test['distress']:.2f} ({'High' if test['distress'] > 0.5 else 'Low'})")

        # Run triage
        result = engine.generate_dispatcher_guidance(
            confidence=test['confidence'],
            distress_score=test['distress'],
            transcript=test['scenario'],
            content_score=test['content']
        )

        # Validate results
        queue_match = result['queue'] == test['expected_queue']
        priority_match = result['priority_level'] == test['expected_priority']
        audio_flag_match = result['flag_audio_review'] == test['should_flag_audio']

        all_match = queue_match and priority_match and audio_flag_match

        print(f"\nExpected:")
        print(f"  Queue:    {test['expected_queue']}")
        print(f"  Priority: {test['expected_priority']}")
        print(f"  Audio Review: {'YES' if test['should_flag_audio'] else 'NO'}")

        print(f"\nActual:")
        print(f"  Queue:    {result['queue']} {'✓' if queue_match else '✗ MISMATCH'}")
        print(f"  Priority: {result['priority_level']} {'✓' if priority_match else '✗ MISMATCH'}")
        print(f"  Audio Review: {'YES' if result['flag_audio_review'] else 'NO'} {'✓' if audio_flag_match else '✗ MISMATCH'}")
        print(f"  Escalate: {'YES' if result['escalation_required'] else 'NO'}")

        print(f"\nReasoning:")
        print(f"  {result['reasoning']}")

        print(f"\nDispatcher Action:")
        print(f"  {result['dispatcher_action']}")

        if all_match:
            print(f"\n✅ TEST CASE {i} PASSED")
            passed += 1
        else:
            print(f"\n❌ TEST CASE {i} FAILED")
            failed += 1

    # Summary
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Tests:  {len(test_cases)}")
    print(f"Passed:       {passed} ✅")
    print(f"Failed:       {failed} {'❌' if failed > 0 else ''}")
    print(f"Success Rate: {(passed/len(test_cases)*100):.1f}%")
    print(f"{'=' * 80}\n")

    return passed, failed


def test_boundary_thresholds():
    """Test threshold boundary conditions"""
    engine = TriageEngine()

    print("\n" + "=" * 80)
    print("THRESHOLD BOUNDARY TESTS")
    print("=" * 80)

    # Test exactly at thresholds
    boundary_tests = [
        # Confidence threshold = 0.7
        {"conf": 0.69, "cont": 0.4, "dist": 0.4, "desc": "Just below confidence threshold"},
        {"conf": 0.70, "cont": 0.4, "dist": 0.4, "desc": "Exactly at confidence threshold"},
        {"conf": 0.71, "cont": 0.4, "dist": 0.4, "desc": "Just above confidence threshold"},

        # Content threshold = 0.5
        {"conf": 0.8, "cont": 0.49, "dist": 0.4, "desc": "Just below content threshold"},
        {"conf": 0.8, "cont": 0.50, "dist": 0.4, "desc": "Exactly at content threshold"},
        {"conf": 0.8, "cont": 0.51, "dist": 0.4, "desc": "Just above content threshold"},

        # Distress threshold = 0.5
        {"conf": 0.8, "cont": 0.4, "dist": 0.49, "desc": "Just below distress threshold"},
        {"conf": 0.8, "cont": 0.4, "dist": 0.50, "desc": "Exactly at distress threshold"},
        {"conf": 0.8, "cont": 0.4, "dist": 0.51, "dist": 0.51, "desc": "Just above distress threshold"},
    ]

    for i, test in enumerate(boundary_tests, 1):
        result = engine.prioritize_call(
            confidence=test['conf'],
            content_score=test['cont'],
            distress_score=test['dist']
        )
        print(f"\n{i}. {test['desc']}")
        print(f"   Conf={test['conf']:.2f}, Cont={test['cont']:.2f}, Dist={test['dist']:.2f}")
        print(f"   → Queue: {result['queue']}, Priority: {result['priority_level']}")


if __name__ == "__main__":
    # Run main 3D matrix test
    passed, failed = test_3d_triage_matrix()

    # Run boundary tests
    test_boundary_thresholds()

    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)
