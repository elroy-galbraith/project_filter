# Live Calls Map Integration - Implementation Summary

## ✅ Problem Solved

Live calls from WebSocket sessions now appear on your map visualization! Previously, live calls were saved to the database but didn't show on the map because they lacked geographic coordinates.

## 🎯 What Was Implemented

### 1. **Database Schema Enhancement**
Added location fields to the `LiveCall` table:
- `location` (String) - Human-readable location (e.g., "Kingston, Jamaica")
- `lat` (Float) - Latitude for map markers
- `lng` (Float) - Longitude for map markers
- `category` (String) - Call classification (e.g., "EMERGENCY CALL", "LIFE SAFETY")

### 2. **Database Migration**
Created automatic migration script that:
- ✅ Adds new columns to existing database
- ✅ Sets default location for existing calls (Jamaica center: 18.1096, -77.2975)
- ✅ Preserves all existing call data

**Run migration:**
```bash
cd backend
python migrate_database.py
```

### 3. **Unified API Endpoint**
Modified `/api/calls` to return **both** mock calls and live calls:

**Before:**
```python
GET /api/calls  # Only returned 4 mock calls
```

**After:**
```python
GET /api/calls  # Returns 8 calls (4 mock + 4 live)
```

Each call now has:
- ✅ Unique ID (`CALL-1042` for mock, `LIVE-3CEB2ED3` for live)
- ✅ Geographic coordinates (lat/lng)
- ✅ Human-readable location
- ✅ Category for color-coding
- ✅ Complete triage data

### 4. **Individual Call Lookup**
Enhanced `/api/calls/{call_id}` to support both mock and live calls:

```bash
# Get mock call
GET /api/calls/CALL-1042

# Get live call
GET /api/calls/LIVE-3CEB2ED3
```

## 📊 Current State

### Your Map Now Shows:

**Mock Calls (🟢 Green markers):**
- CALL-1042 - Nelson St, Kingston (18.0269, -77.8486)
- CALL-1043 - Santa Cruz, St. Elizabeth (18.0567, -77.8972)
- CALL-1044 - Savanna-la-Mar, Westmoreland (18.2186, -78.1319)
- CALL-1045 - Unknown - Cell Tower: New Hope, St. Elizabeth (18.045, -77.82)

**Live Calls (🔴 Red markers):**
- LIVE-TEST1234 - Jamaica (Location not specified) (18.1096, -77.2975)
- LIVE-13183CE1 - Jamaica (Location not specified) (18.1096, -77.2975)
- LIVE-E860892C - Jamaica (Location not specified) (18.1096, -77.2975)
- LIVE-3CEB2ED3 - Jamaica (Location not specified) (18.1096, -77.2975)

**Total: 8 calls visible on map**

## 🚀 How It Works

### Call Flow
```
Live WebSocket Call
    ↓
Processing (ASR + Bio-Acoustic + Triage)
    ↓
Save to Database (with default location)
    ↓
GET /api/calls (combines mock + live)
    ↓
Frontend Map (displays all markers)
```

### Default Behavior
Live calls without explicit location data get:
- **Location**: "Jamaica (Location not specified)"
- **Coordinates**: 18.1096, -77.2975 (Jamaica center)
- **Category**: "EMERGENCY CALL"

This ensures **all calls appear on the map**, even if location isn't provided.

## 🔧 Files Modified

### Database Layer
- [backend/database.py](../backend/database.py:73-77) - Added location columns
- [backend/migrate_database.py](../backend/migrate_database.py) - Migration script

### API Layer
- [backend/main.py](../backend/main.py:77-116) - Updated `/api/calls` endpoint
- [backend/main.py](../backend/main.py:119-155) - Updated `/api/calls/{call_id}` endpoint

### Testing
- [backend/test_unified_calls.py](../backend/test_unified_calls.py) - Verification script

## 💡 Future Enhancements

### Option 1: NLP Location Extraction
Extract location from transcript:
```python
# In live_processor.py
def extract_location(transcript):
    # Use NLP to find "Kingston", "Santa Cruz", etc.
    # Geocode to lat/lng
    return location, lat, lng
```

### Option 2: Cell Tower Geolocation
Use phone metadata for approximate location:
```python
# In live_processor.py
def get_cell_tower_location(phone_metadata):
    # Map cell tower ID to coordinates
    return lat, lng
```

### Option 3: Manual Location Entry
Let dispatchers add location via UI after call:
```python
PATCH /api/live-calls/{call_id}
{
  "location": "Nelson Street, Kingston",
  "lat": 18.0269,
  "lng": -77.8486
}
```

## 🧪 Testing

### Verify Map Integration

1. **Start the server:**
```bash
cd backend
uvicorn main:app --reload
```

2. **Check unified endpoint:**
```bash
curl http://localhost:8000/api/calls | python -m json.tool
```

You should see 8 calls total (4 mock + 4 live).

3. **Check specific live call:**
```bash
curl http://localhost:8000/api/calls/LIVE-3CEB2ED3
```

Should return complete call data with coordinates.

4. **Run test script:**
```bash
cd backend
python test_unified_calls.py
```

Expected output:
```
✅ Total calls for map: 8
   - Mock calls: 4
   - Live calls: 4
```

### Frontend Testing

Your React/Vue frontend should now:
1. Fetch `/api/calls`
2. Receive 8 calls (mock + live)
3. Display all markers on map
4. Show live calls at Jamaica center (18.1096, -77.2975)

**Distinguishing Live vs Mock Calls:**
```javascript
// In frontend code
calls.forEach(call => {
    const isLive = call.id.startsWith('LIVE-');
    const markerColor = isLive ? 'red' : 'green';
    // Add marker to map...
});
```

## 📝 API Response Format

### GET /api/calls (Unified)

```json
[
  {
    "id": "CALL-1042",
    "time": "14:02:15",
    "audio_file": "assets/call_1_calm.wav",
    "transcript": "Reporting a downed utility pole...",
    "confidence": 0.92,
    "pitch_avg": 135,
    "energy_avg": 0.02,
    "distress_score": 15,
    "is_distress": false,
    "status": "AUTO-LOGGED",
    "location": "Nelson St, Kingston",
    "category": "Infrastructure: Power",
    "lat": 18.0269,
    "lng": -77.8486,
    "nlp_extraction": { ... }
  },
  {
    "id": "LIVE-3CEB2ED3",
    "time": "14:05:02",
    "audio_file": "",
    "transcript": "I am testing Trident...",
    "confidence": 0.3,
    "pitch_avg": 150,
    "energy_avg": 0.0,
    "distress_score": 52,
    "is_distress": true,
    "status": "Q1-IMMEDIATE",
    "location": "Jamaica (Location not specified)",
    "category": "EMERGENCY CALL",
    "lat": 18.1096,
    "lng": -77.2975,
    "nlp_extraction": null
  }
]
```

## ✅ Summary

Your TRIDENT system now has **complete map integration** for live calls:

✅ Live calls automatically saved to database
✅ Location fields added with sensible defaults
✅ Unified `/api/calls` endpoint combines mock + live calls
✅ All calls have coordinates and appear on map
✅ Individual call lookup supports both mock and live
✅ Database migration preserves existing data

**No more invisible calls!** Every live WebSocket session now appears on your map visualization. 🗺️🎯
