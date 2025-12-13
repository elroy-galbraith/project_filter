"""
Test script to verify database persistence for live calls.

This script tests:
1. Database connection
2. Creating a mock live call record
3. Querying saved records
4. Verifying data integrity
"""

from datetime import datetime
from database import SessionLocal, LiveCall, init_db

def test_database():
    """Test database functionality."""

    # Initialize database
    print("Initializing database...")
    init_db()
    print("✓ Database initialized\n")

    # Create session
    db = SessionLocal()

    try:
        # Create a test live call record
        print("Creating test live call record...")
        test_call = LiveCall(
            call_id="LIVE-TEST1234",
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=45.5,
            chunks_processed=15,
            total_audio_duration=43.2,
            transcript="This is a test emergency call from the database test script.",
            confidence_score=0.87,
            distress_score=35.2,
            pitch_mean_hz=145.5,
            pitch_cv=0.12,
            energy_rms=0.045,
            jitter=0.008,
            triage_queue="auto_logged",
            priority_level=3,
            flag_audio_review=False,
            escalation_required=False,
            dispatcher_action="Log and route to infrastructure team",
            triage_reasoning="Low distress score, high confidence transcript",
            triage_data={
                "queue": "auto_logged",
                "priority_level": 3,
                "reasoning": "Test call with normal parameters"
            },
            status="completed"
        )

        db.add(test_call)
        db.commit()
        db.refresh(test_call)

        print(f"✓ Test call created with ID: {test_call.id}")
        print(f"  Call ID: {test_call.call_id}")
        print(f"  Transcript: {test_call.transcript[:50]}...")
        print(f"  Queue: {test_call.triage_queue}")
        print(f"  Confidence: {test_call.confidence_score:.2f}")
        print(f"  Distress: {test_call.distress_score:.2f}\n")

        # Query all live calls
        print("Querying all live calls...")
        all_calls = db.query(LiveCall).all()
        print(f"✓ Found {len(all_calls)} total live call(s) in database\n")

        # Display all calls
        for i, call in enumerate(all_calls, 1):
            print(f"{i}. {call.call_id} - Queue: {call.triage_queue}, "
                  f"Confidence: {call.confidence_score:.2f}, "
                  f"Distress: {call.distress_score:.2f}")

        print("\n✅ Database test completed successfully!")
        print(f"Database location: backend/trident_calls.db")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    test_database()
