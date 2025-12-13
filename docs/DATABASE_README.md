# TRIDENT Live Call Database Persistence

## Overview

Live call data from WebSocket sessions is now automatically saved to a SQLite database for persistent storage and analysis. This allows you to:

- **Review past calls** after WebSocket disconnection
- **Query and filter** calls by triage queue, confidence, distress score
- **Analyze trends** across multiple emergency calls
- **Audit trail** for all live processing sessions

## Database Schema

### LiveCall Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary key (auto-increment) |
| `call_id` | String | Unique call identifier (e.g., "LIVE-A1B2C3D4") |
| `start_time` | DateTime | Call start timestamp |
| `end_time` | DateTime | Call end timestamp |
| `duration_seconds` | Float | Total call duration |
| `chunks_processed` | Integer | Number of audio chunks processed |
| `total_audio_duration` | Float | Total audio duration (seconds) |
| `transcript` | Text | Complete ASR transcript |
| `confidence_score` | Float | ASR confidence (0.0 - 1.0) |
| `distress_score` | Float | Bio-acoustic distress score (0.0 - 100.0) |
| `pitch_mean_hz` | Float | Average pitch (Hz) |
| `pitch_cv` | Float | Pitch coefficient of variation |
| `energy_rms` | Float | RMS energy |
| `jitter` | Float | Voice jitter |
| `triage_queue` | String | Assigned queue ("auto_logged", "human_review", "priority_dispatch") |
| `priority_level` | Integer | Priority level (1=highest, 5=lowest) |
| `flag_audio_review` | Boolean | Flagged for audio review |
| `escalation_required` | Boolean | Requires escalation |
| `dispatcher_action` | Text | Recommended dispatcher action |
| `triage_reasoning` | Text | Triage decision reasoning |
| `triage_data` | JSON | Complete triage result object |
| `status` | String | Call status ("completed", "error", "interrupted") |
| `error_message` | Text | Error details (if any) |
| `created_at` | DateTime | Record creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

## API Endpoints

### 1. Get All Live Calls

```http
GET /api/live-calls?limit=50&offset=0&queue=auto_logged
```

**Query Parameters:**
- `limit` (optional): Maximum records to return (default: 50)
- `offset` (optional): Records to skip for pagination (default: 0)
- `queue` (optional): Filter by triage queue

**Response:**
```json
{
  "total": 150,
  "count": 50,
  "calls": [
    {
      "id": 1,
      "call_id": "LIVE-A1B2C3D4",
      "start_time": "2025-12-13T14:30:15",
      "end_time": "2025-12-13T14:31:00",
      "duration_seconds": 45.2,
      "transcript": "Reporting flooding on Main Street...",
      "confidence_score": 0.89,
      "distress_score": 28.5,
      "triage_queue": "auto_logged",
      "priority_level": 3,
      "flag_audio_review": false,
      "escalation_required": false,
      "dispatcher_action": "Log incident and dispatch infrastructure team",
      "triage_reasoning": "Clear communication, low distress indicators",
      "chunks_processed": 15,
      "status": "completed"
    }
  ]
}
```

### 2. Get Specific Live Call

```http
GET /api/live-calls/{call_id}
```

**Response:**
```json
{
  "id": 1,
  "call_id": "LIVE-A1B2C3D4",
  "start_time": "2025-12-13T14:30:15",
  "end_time": "2025-12-13T14:31:00",
  "duration_seconds": 45.2,
  "transcript": "Reporting flooding on Main Street...",
  "confidence_score": 0.89,
  "distress_score": 28.5,
  "bio_acoustic": {
    "pitch_mean_hz": 145.2,
    "pitch_cv": 0.12,
    "energy_rms": 0.045,
    "jitter": 0.008
  },
  "triage": {
    "queue": "auto_logged",
    "priority_level": 3,
    "flag_audio_review": false,
    "escalation_required": false,
    "dispatcher_action": "Log incident and dispatch infrastructure team",
    "reasoning": "Clear communication, low distress indicators"
  },
  "triage_queue": "auto_logged",
  "priority_level": 3,
  "flag_audio_review": false,
  "escalation_required": false,
  "dispatcher_action": "Log incident and dispatch infrastructure team",
  "triage_reasoning": "Clear communication, low distress indicators",
  "chunks_processed": 15,
  "total_audio_duration": 43.5,
  "status": "completed",
  "created_at": "2025-12-13T14:31:00"
}
```

### 3. Health Check (Updated)

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "total_calls": 4,
  "live_calls_saved": 25
}
```

## Usage Examples

### Python Client

```python
import requests

# Get all live calls
response = requests.get('http://localhost:8000/api/live-calls')
calls = response.json()['calls']

# Filter by queue
response = requests.get('http://localhost:8000/api/live-calls?queue=human_review')
review_calls = response.json()['calls']

# Get specific call
response = requests.get('http://localhost:8000/api/live-calls/LIVE-A1B2C3D4')
call_details = response.json()
```

### JavaScript/Fetch

```javascript
// Get all live calls
const response = await fetch('http://localhost:8000/api/live-calls');
const data = await response.json();
console.log(`Found ${data.total} calls`);

// Filter by queue
const reviewCalls = await fetch('http://localhost:8000/api/live-calls?queue=human_review');
const reviewData = await reviewCalls.json();

// Get specific call
const callResponse = await fetch('http://localhost:8000/api/live-calls/LIVE-A1B2C3D4');
const callData = await callResponse.json();
```

### cURL

```bash
# Get all live calls
curl http://localhost:8000/api/live-calls

# Filter by queue
curl "http://localhost:8000/api/live-calls?queue=priority_dispatch"

# Pagination
curl "http://localhost:8000/api/live-calls?limit=10&offset=20"

# Get specific call
curl http://localhost:8000/api/live-calls/LIVE-A1B2C3D4
```

## Direct Database Access

### Using Python

```python
from database import SessionLocal, LiveCall
from sqlalchemy import func

db = SessionLocal()

# Get all calls
all_calls = db.query(LiveCall).all()

# Filter by queue
auto_logged = db.query(LiveCall).filter(
    LiveCall.triage_queue == "auto_logged"
).all()

# High distress calls
high_distress = db.query(LiveCall).filter(
    LiveCall.distress_score > 70
).all()

# Recent calls (last 24 hours)
from datetime import datetime, timedelta
recent = db.query(LiveCall).filter(
    LiveCall.start_time > datetime.now() - timedelta(days=1)
).all()

# Statistics
avg_confidence = db.query(func.avg(LiveCall.confidence_score)).scalar()
avg_distress = db.query(func.avg(LiveCall.distress_score)).scalar()

db.close()
```

### Using SQLite CLI

```bash
# Open database
sqlite3 backend/trident_calls.db

# View all calls
SELECT call_id, triage_queue, confidence_score, distress_score
FROM live_calls
ORDER BY start_time DESC
LIMIT 10;

# Count by queue
SELECT triage_queue, COUNT(*)
FROM live_calls
GROUP BY triage_queue;

# Average metrics
SELECT
    AVG(confidence_score) as avg_confidence,
    AVG(distress_score) as avg_distress,
    COUNT(*) as total_calls
FROM live_calls;
```

## Automatic Persistence

Every live call is **automatically saved** when the WebSocket session ends:

1. **During live processing**: Audio chunks are processed in real-time
2. **When call ends**: The `finalize()` method saves the complete record to the database
3. **Error handling**: Database failures won't crash the session (errors are logged)

No manual intervention required - just make live calls and they'll be persisted!

## Database Location

- **Development**: `backend/trident_calls.db` (SQLite file)
- **Production**: Configure via `DATABASE_URL` environment variable

```bash
# Use PostgreSQL in production
export DATABASE_URL="postgresql://user:password@host:5432/trident"
```

## Testing

Run the test script to verify database functionality:

```bash
cd backend
python test_database.py
```

This will:
1. Initialize the database
2. Create a test live call record
3. Query and display saved records
4. Verify data integrity

## Migration Notes

If you need to update the database schema:

```python
# 1. Drop existing tables (CAUTION: Data loss!)
from database import Base, engine
Base.metadata.drop_all(bind=engine)

# 2. Recreate with new schema
Base.metadata.create_all(bind=engine)
```

For production, use migration tools like **Alembic** for safe schema updates.

## Performance Considerations

- **SQLite** is suitable for development and small-scale deployments
- For **high-volume production**, consider PostgreSQL or MySQL
- Database writes are **non-blocking** - they won't delay WebSocket responses
- Queries are indexed on `call_id` and `start_time` for fast lookups

## Troubleshooting

### Database file not found
```bash
# Ensure you're in the backend directory
cd backend
python -c "from database import init_db; init_db()"
```

### Import errors
```bash
# Install SQLAlchemy
pip install sqlalchemy>=2.0.0
```

### Permission errors
```bash
# Ensure write permissions
chmod 664 trident_calls.db
```

## Future Enhancements

Potential improvements:
- **Audio file storage**: Save raw audio files alongside records
- **Search functionality**: Full-text search on transcripts
- **Analytics dashboard**: Visualize trends and patterns
- **Export features**: CSV/JSON export for external analysis
- **Retention policies**: Automatic cleanup of old records
