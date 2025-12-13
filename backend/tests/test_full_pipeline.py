"""
End-to-End Integration Test for Complete TRIDENT Pipeline

Tests all three layers working together:
1. Layer 1 (ASR): Speech recognition + confidence
2. Layer 2 (NLP): Entity extraction + content scoring
3. Layer 3 (Bio-Acoustic): Distress detection
4. Triage: 3D decision matrix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_processor import BioAcousticProcessor
from asr_service import ASRService
from nlp_service import NLPService
from triage_engine import TriageEngine
import json


def test_full_pipeline():
    """Test complete TRIDENT pipeline with sample audio files"""

    # Initialize all services
    print("\n" + "=" * 80)
    print("INITIALIZING TRIDENT SERVICES")
    print("=" * 80)

    bio_processor = BioAcousticProcessor()
    print("✓ Bio-Acoustic Processor initialized")

    asr_service = ASRService()
    print("✓ ASR Service initialized (loading Whisper + LoRA...)")

    nlp_service = NLPService()
    print("✓ NLP Service initialized (Ollama + Llama 3)")

    triage_engine = TriageEngine()
    print("✓ Triage Engine initialized")

    # Test audio files
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "assets")
    test_files = [
        "call_1_calm.wav",
        "call_2_moderate.wav",
        "call_3_urgent.wav",
        "call_4_panic.wav"
    ]

    results = []

    print("\n" + "=" * 80)
    print("PROCESSING TEST AUDIO FILES")
    print("=" * 80)

    for i, filename in enumerate(test_files, 1):
        filepath = os.path.join(assets_dir, filename)

        if not os.path.exists(filepath):
            print(f"\n⚠️  File not found: {filepath}")
            continue

        print(f"\n{'─' * 80}")
        print(f"TEST {i}/{len(test_files)}: {filename}")
        print(f"{'─' * 80}")

        try:
            # Layer 1: ASR
            print(f"  [1/4] Running ASR...")
            asr_result = asr_service.transcribe_with_confidence(filepath)
            print(f"        Transcript: \"{asr_result['transcript'][:80]}...\"")
            print(f"        Confidence: {asr_result['confidence']:.3f}")

            # Layer 2: NLP
            print(f"  [2/4] Running NLP entity extraction...")
            nlp_result = nlp_service.extract_entities(
                transcript=asr_result['transcript'],
                confidence=asr_result['confidence']
            )
            print(f"        Hazard Type: {nlp_result['entities']['mechanism_hazard']}")
            print(f"        Content Score: {nlp_result['content_score']:.3f}")

            # Layer 3: Bio-Acoustic
            print(f"  [3/4] Running bio-acoustic analysis...")
            bio_result = bio_processor.extract_features(filepath)
            print(f"        F0 Mean: {bio_result.get('f0_mean', 0):.1f} Hz")
            print(f"        Distress Score: {bio_result['distress_score']:.3f}")

            # Triage Decision
            print(f"  [4/4] Generating triage decision...")
            triage_result = triage_engine.generate_dispatcher_guidance(
                confidence=asr_result['confidence'],
                distress_score=bio_result['distress_score'],
                transcript=asr_result['transcript'],
                content_score=nlp_result['content_score']
            )

            # Display results
            print(f"\n  📊 TRIAGE DECISION:")
            print(f"     Queue: {triage_result['queue']} (Priority {triage_result['priority_level']})")
            print(f"     Audio Review: {'YES' if triage_result['flag_audio_review'] else 'NO'}")
            print(f"     Escalation: {'YES' if triage_result['escalation_required'] else 'NO'}")
            print(f"\n  💡 REASONING:")
            print(f"     {triage_result['reasoning']}")
            print(f"\n  🎯 DISPATCHER ACTION:")
            print(f"     {triage_result['dispatcher_action']}")

            # Extract location if present
            location = nlp_result['entities'].get('location', {})
            if location.get('address') or location.get('landmark') or location.get('geographic_ref'):
                print(f"\n  📍 LOCATION EXTRACTED:")
                if location.get('address'):
                    print(f"     Address: {location['address']}")
                if location.get('landmark'):
                    print(f"     Landmark: {location['landmark']}")
                if location.get('geographic_ref'):
                    print(f"     Area: {location['geographic_ref']}")

            # Extract clinical indicators if present
            clinical = nlp_result['entities'].get('clinical_indicators', {})
            if any(v != 'unknown' for v in clinical.values()):
                print(f"\n  🏥 CLINICAL INDICATORS:")
                for key, value in clinical.items():
                    if value != 'unknown':
                        print(f"     {key.capitalize()}: {value}")

            results.append({
                "file": filename,
                "confidence": asr_result['confidence'],
                "content_score": nlp_result['content_score'],
                "distress_score": bio_result['distress_score'],
                "queue": triage_result['queue'],
                "priority": triage_result['priority_level'],
                "hazard": nlp_result['entities']['mechanism_hazard']
            })

            print(f"\n  ✅ Processing complete")

        except Exception as e:
            print(f"\n  ❌ Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print(f"\n{'=' * 80}")
    print("PIPELINE TEST SUMMARY")
    print(f"{'=' * 80}")
    print(f"Files processed: {len(results)}/{len(test_files)}")
    print(f"\nResults table:")
    print(f"{'─' * 80}")
    print(f"{'File':<20} {'Queue':<15} {'Pri':<5} {'Conf':<6} {'Cont':<6} {'Dist':<6}")
    print(f"{'─' * 80}")

    for r in results:
        print(f"{r['file']:<20} {r['queue']:<15} {r['priority']:<5} "
              f"{r['confidence']:<6.2f} {r['content_score']:<6.2f} {r['distress_score']:<6.2f}")

    print(f"{'─' * 80}")

    # Count by queue
    queue_counts = {}
    for r in results:
        queue = r['queue']
        queue_counts[queue] = queue_counts.get(queue, 0) + 1

    print(f"\nQueue distribution:")
    for queue, count in sorted(queue_counts.items()):
        print(f"  {queue}: {count}")

    print(f"{'=' * 80}\n")

    return len(results) == len(test_files)


def test_nlp_only():
    """Test NLP service with synthetic transcripts"""

    nlp_service = NLPService()

    print("\n" + "=" * 80)
    print("NLP SERVICE STANDALONE TEST")
    print("=" * 80)

    test_transcripts = [
        {
            "text": "There's a massive fire at 123 King Street! Multiple people trapped inside, I can see smoke everywhere!",
            "confidence": 0.95,
            "expected_hazard": "fire",
            "expected_high_content": True
        },
        {
            "text": "Man down by di market, him nah breathe right, blood all over di place, please send help quick!",
            "confidence": 0.45,
            "expected_hazard": "medical",
            "expected_high_content": True
        },
        {
            "text": "Just reporting a small pothole on Main Road near the church",
            "confidence": 0.92,
            "expected_hazard": "infrastructure",
            "expected_high_content": False
        }
    ]

    for i, test in enumerate(test_transcripts, 1):
        print(f"\n{'─' * 80}")
        print(f"NLP Test {i}")
        print(f"{'─' * 80}")
        print(f"Transcript: \"{test['text']}\"")
        print(f"Confidence: {test['confidence']:.2f}")

        result = nlp_service.extract_entities(test['text'], test['confidence'])

        print(f"\nExtracted Entities:")
        print(json.dumps(result['entities'], indent=2))
        print(f"\nContent Score: {result['content_score']:.2f}")

        # Validate
        hazard_match = result['entities']['mechanism_hazard'] == test['expected_hazard']
        content_high = result['content_score'] > 0.5

        print(f"\nValidation:")
        hazard_status = "✓" if hazard_match else f"✗ (expected {test['expected_hazard']})"
        print(f"  Hazard type: {result['entities']['mechanism_hazard']} {hazard_status}")
        content_status = "✓" if content_high == test['expected_high_content'] else "✗"
        print(f"  High content: {'Yes' if content_high else 'No'} {content_status}")


if __name__ == "__main__":
    # Run NLP standalone test first (faster)
    print("\n" + "🧪 STARTING TRIDENT FULL PIPELINE TESTS" + "\n")

    test_nlp_only()

    # Run full pipeline test
    success = test_full_pipeline()

    print("\n✅ All tests complete!\n" if success else "\n⚠️ Some tests failed\n")

    sys.exit(0 if success else 1)
