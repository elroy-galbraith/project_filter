"""
TRIDENT End-to-End Pipeline Testing

Tests the complete TRIDENT processing pipeline with all 4 sample audio files
from the PRD test scenarios.

Test Cases:
1. CALL-1042: Calm acrolect (high confidence, low distress) → Q5-ROUTINE
2. CALL-1043: Calm infrastructure (high confidence, low distress) → Q5-ROUTINE
3. CALL-1044: Calm service outage (high confidence, low distress) → Q5-ROUTINE
4. CALL-1045: HERO SCENARIO - Stressed basilect (low confidence, high distress) → Q1-IMMEDIATE

Validates:
- ASR confidence scoring
- Bio-acoustic distress detection
- Triage decision logic
- Integration between all components
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from audio_processor import BioAcousticProcessor
from asr_service import ASRService
from triage_engine import TriageEngine


def test_audio_file(audio_path: str, expected_scenario: dict):
    """
    Test complete pipeline on a single audio file.

    Args:
        audio_path: Path to audio file
        expected_scenario: Dict with expected outcomes for validation
    """
    print(f"\n{'='*80}")
    print(f"Testing: {os.path.basename(audio_path)}")
    print(f"Expected: {expected_scenario['description']}")
    print(f"{'='*80}")

    # Initialize services
    bio_processor = BioAcousticProcessor()
    asr_service = ASRService()
    triage_engine = TriageEngine()

    try:
        # Layer 3: Bio-Acoustic Analysis
        print("\n[1/3] Running bio-acoustic analysis...")
        bio_result = bio_processor.extract_features(audio_path)

        print(f"  ✓ F0 Mean:        {bio_result['f0_mean']:.1f} Hz")
        print(f"  ✓ F0 CV:          {bio_result['f0_cv']:.3f}")
        print(f"  ✓ Energy:         {bio_result['energy']:.3f}")
        print(f"  ✓ Distress Score: {bio_result['distress_score']:.3f}")

        # Layer 1: ASR with Confidence
        print("\n[2/3] Running ASR with confidence scoring...")
        asr_result = asr_service.transcribe_with_confidence(audio_path)

        print(f"  ✓ Confidence:     {asr_result['confidence']:.3f} ({asr_result['confidence']*100:.1f}%)")
        print(f"  ✓ Transcript:     {asr_result['transcript'][:100]}...")

        # Triage Decision
        print("\n[3/3] Generating triage decision...")
        triage_result = triage_engine.generate_dispatcher_guidance(
            confidence=asr_result['confidence'],
            distress_score=bio_result['distress_score'],
            transcript=asr_result['transcript']
        )

        print(f"  ✓ Queue:          {triage_result['queue']}")
        print(f"  ✓ Priority Level: {triage_result['priority_level']}")
        print(f"  ✓ Audio Review:   {'YES' if triage_result['flag_audio_review'] else 'NO'}")
        print(f"  ✓ Escalate:       {'YES' if triage_result['escalation_required'] else 'NO'}")

        # Validation
        print(f"\n{'─'*80}")
        print("VALIDATION:")

        # Check expected queue
        if triage_result['queue'] == expected_scenario['expected_queue']:
            print(f"  ✓ Queue routing CORRECT: {triage_result['queue']}")
        else:
            print(f"  ✗ Queue routing INCORRECT:")
            print(f"    Expected: {expected_scenario['expected_queue']}")
            print(f"    Got:      {triage_result['queue']}")

        # Check confidence threshold
        if expected_scenario.get('high_confidence'):
            if asr_result['confidence'] >= 0.7:
                print(f"  ✓ High confidence CONFIRMED: {asr_result['confidence']:.3f}")
            else:
                print(f"  ⚠ Expected high confidence, got: {asr_result['confidence']:.3f}")
        else:
            if asr_result['confidence'] < 0.7:
                print(f"  ✓ Low confidence CONFIRMED: {asr_result['confidence']:.3f}")
            else:
                print(f"  ⚠ Expected low confidence, got: {asr_result['confidence']:.3f}")

        # Check distress threshold
        if expected_scenario.get('high_distress'):
            if bio_result['distress_score'] > 0.5:
                print(f"  ✓ High distress CONFIRMED: {bio_result['distress_score']:.3f}")
            else:
                print(f"  ⚠ Expected high distress, got: {bio_result['distress_score']:.3f}")
        else:
            if bio_result['distress_score'] <= 0.5:
                print(f"  ✓ Low distress CONFIRMED: {bio_result['distress_score']:.3f}")
            else:
                print(f"  ⚠ Expected low distress, got: {bio_result['distress_score']:.3f}")

        print(f"\n{'─'*80}")
        print("REASONING:")
        print(f"  {triage_result['reasoning']}")

        print(f"\nDISPATCHER ACTION:")
        print(f"  {triage_result['dispatcher_action']}")

        return {
            "success": True,
            "bio_acoustic": bio_result,
            "asr": asr_result,
            "triage": triage_result
        }

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def main():
    """Run complete test suite on all sample audio files."""
    print("\n" + "█" * 80)
    print("TRIDENT END-TO-END PIPELINE TEST SUITE")
    print("Testing: ASR + Bio-Acoustic + Triage Decision")
    print("█" * 80)

    # Define test scenarios (from PRD and mock data)
    test_scenarios = [
        {
            "file": "../assets/call_1_calm.wav",
            "description": "Calm infrastructure report (Black River utility pole)",
            "expected_queue": "Q5-ROUTINE",
            "high_confidence": True,
            "high_distress": False
        },
        {
            "file": "../assets/call_2_calm.wav",
            "description": "Calm flooding report (Santa Cruz bridge)",
            "expected_queue": "Q5-ROUTINE",
            "high_confidence": True,
            "high_distress": False
        },
        {
            "file": "../assets/call_3_calm.wav",
            "description": "Calm service outage (Savanna-la-Mar water)",
            "expected_queue": "Q5-ROUTINE",
            "high_confidence": True,
            "high_distress": False
        },
        {
            "file": "../assets/call_4_panic.wav",
            "description": "HERO SCENARIO - Distressed basilect (New Hope roof rescue)",
            "expected_queue": "Q1-IMMEDIATE",
            "high_confidence": False,
            "high_distress": True
        }
    ]

    results = []
    passed = 0
    failed = 0

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n\n{'▓'*80}")
        print(f"TEST {i}/{len(test_scenarios)}")
        print(f"{'▓'*80}")

        if not os.path.exists(scenario["file"]):
            print(f"✗ Audio file not found: {scenario['file']}")
            failed += 1
            continue

        result = test_audio_file(scenario["file"], scenario)
        results.append(result)

        if result.get("success"):
            # Check if queue matches expected
            if result["triage"]["queue"] == scenario["expected_queue"]:
                passed += 1
                print(f"\n✓ TEST {i} PASSED")
            else:
                failed += 1
                print(f"\n✗ TEST {i} FAILED (incorrect queue routing)")
        else:
            failed += 1
            print(f"\n✗ TEST {i} FAILED (processing error)")

    # Summary
    print(f"\n\n{'█'*80}")
    print("TEST SUITE SUMMARY")
    print(f"{'█'*80}")
    print(f"\nTotal Tests:  {len(test_scenarios)}")
    print(f"Passed:       {passed} ✓")
    print(f"Failed:       {failed} ✗")
    print(f"Success Rate: {(passed/len(test_scenarios)*100):.1f}%")

    if passed == len(test_scenarios):
        print("\n🎉 ALL TESTS PASSED! TRIDENT pipeline is working correctly.")
        print("\nKey Insights Validated:")
        print("  ✓ ASR confidence scoring operational")
        print("  ✓ Bio-acoustic distress detection functional")
        print("  ✓ Triage routing logic correct")
        print("  ✓ 'ASR failure is a feature' principle demonstrated")
    else:
        print(f"\n⚠ {failed} test(s) failed - review results above")

    print(f"\n{'█'*80}\n")

    return passed == len(test_scenarios)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
