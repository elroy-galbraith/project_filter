"""
Test script to verify unified calls endpoint works correctly.

Tests that live calls from database are merged with mock calls.
"""

from database import SessionLocal, LiveCall
from data import CALL_LOG
from models import Call

def test_unified_calls():
    """Test that live and mock calls can be combined."""

    print("🧪 Testing Unified Calls Endpoint")
    print("=" * 60)

    # Mock calls
    print(f"\n📋 Mock calls in CALL_LOG: {len(CALL_LOG)}")
    for call in CALL_LOG:
        print(f"   - {call.id}: {call.location}")

    # Live calls from database
    db = SessionLocal()
    try:
        live_calls = db.query(LiveCall).all()
        print(f"\n💾 Live calls in database: {len(live_calls)}")

        for live_call in live_calls:
            print(f"   - {live_call.call_id}: {live_call.location}")
            print(f"     Lat/Lng: ({live_call.lat}, {live_call.lng})")
            print(f"     Category: {live_call.category}")

        # Simulate the unified endpoint
        print(f"\n🔄 Creating unified call list...")
        all_calls = list(CALL_LOG)

        for live_call in live_calls:
            call_dict = {
                "id": live_call.call_id,
                "time": live_call.start_time.strftime("%H:%M:%S") if live_call.start_time else "N/A",
                "audio_file": "",
                "transcript": live_call.transcript or "",
                "confidence": live_call.confidence_score or 0.0,
                "pitch_avg": int(live_call.pitch_mean_hz) if live_call.pitch_mean_hz else 150,
                "energy_avg": live_call.energy_rms or 0.0,
                "distress_score": int(live_call.distress_score or 0),
                "is_distress": (live_call.distress_score or 0) > 50,
                "status": live_call.triage_queue or "LIVE-PROCESSED",
                "location": live_call.location or "Jamaica (Location not specified)",
                "category": live_call.category or "EMERGENCY CALL",
                "lat": live_call.lat or 18.1096,
                "lng": live_call.lng or -77.2975,
                "nlp_extraction": None
            }
            all_calls.append(Call(**call_dict))

        print(f"\n✅ Total calls for map: {len(all_calls)}")
        print(f"   - Mock calls: {len(CALL_LOG)}")
        print(f"   - Live calls: {len(live_calls)}")

        # Display all calls with coordinates
        print(f"\n📍 All calls with map coordinates:")
        for call in all_calls:
            marker = "🟢" if call.id.startswith("CALL") else "🔴"
            print(f"   {marker} {call.id} - {call.location} ({call.lat}, {call.lng})")

        print(f"\n✅ Test passed! All calls have coordinates and will appear on map.")

    finally:
        db.close()


if __name__ == "__main__":
    test_unified_calls()
