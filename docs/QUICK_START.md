# TRIDENT Quick Start Guide

## Running the System

### 1. Start the Backend API

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

### 2. Test the Pipeline

**Option A: Run automated test suite**
```bash
cd backend
source venv/bin/activate
python test_pipeline.py
```

**Option B: Test individual components**

Bio-acoustic processor:
```bash
python audio_processor.py ../assets/call_1_calm.wav
```

ASR service:
```bash
python asr_service.py ../assets/call_1_calm.wav
```

Triage engine:
```bash
python triage_engine.py
```

### 3. Test the API Endpoint

Using curl:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@assets/call_1_calm.wav"
```

Using Python requests:
```python
import requests

with open("../assets/call_1_calm.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        files={"file": f}
    )

print(response.json())
```

### 4. View API Documentation

Interactive API docs: `http://localhost:8000/docs`

## Expected Response Format

```json
{
  "transcript": "Yes, I want to report...",
  "confidence": 0.85,
  "bio_acoustic": {
    "f0_mean": 169.2,
    "f0_cv": 0.345,
    "pitch_elevation": 0.052,
    "instability": 0.690,
    "energy": 0.703,
    "jitter": 0.021,
    "distress_score": 0.532
  },
  "triage": {
    "queue": "Q1-IMMEDIATE",
    "priority_level": 1,
    "flag_audio_review": true,
    "reasoning": "Low ASR confidence + high bio-acoustic distress...",
    "dispatcher_action": "IMMEDIATE ATTENTION REQUIRED: Listen to audio...",
    "escalation_required": true
  }
}
```

## Understanding the Output

### Confidence Score (0-1)
- **>0.7** = High confidence (clear transcription)
- **<0.7** = Low confidence (needs review)

### Distress Score (0-1)
- **>0.5** = High distress (elevated stress indicators)
- **≤0.5** = Low distress (calm delivery)

### Priority Queues
- **Q1-IMMEDIATE** (Priority 1) - Critical, needs immediate attention
- **Q3-MONITOR** (Priority 3) - Elevated concern, monitor situation
- **Q5-REVIEW** (Priority 5) - Low confidence, verify when able
- **Q5-ROUTINE** (Priority 5) - Standard logging, no urgency

## Triage Decision Matrix

| Confidence | Distress | Queue | Action |
|------------|----------|-------|--------|
| Low | High | Q1-IMMEDIATE | IMMEDIATE review + escalate |
| High | High | Q3-MONITOR | Monitor situation |
| Low | Low | Q5-REVIEW | Review when available |
| High | Low | Q5-ROUTINE | Standard logging |

## Troubleshooting

### Model Loading Issues

If you see "LoRA adapter not found":
```bash
# Check if model files exist
ls -la backend/model_full/
```

Files should include:
- adapter_model.safetensors
- adapter_config.json
- tokenizer.json

### Memory Issues

If Whisper model won't load:
- Close other applications
- Ensure 8GB+ RAM available
- Model requires ~3GB for Whisper Large

### Slow Processing

Expected processing times:
- First call: 10-15 seconds (model loading)
- Subsequent calls: 6-11 seconds each
- Bio-acoustic: <1 second
- ASR: 5-10 seconds

## Sample Audio Files

Test with provided samples:

```bash
# Calm infrastructure reports (should route to Q5-ROUTINE)
curl -X POST http://localhost:8000/api/analyze -F "file=@assets/call_1_calm.wav"
curl -X POST http://localhost:8000/api/analyze -F "file=@assets/call_2_calm.wav"
curl -X POST http://localhost:8000/api/analyze -F "file=@assets/call_3_calm.wav"

# Distress call (should route to Q1-IMMEDIATE)
curl -X POST http://localhost:8000/api/analyze -F "file=@assets/call_4_panic.wav"
```

**Note:** Due to confidence scoring workaround and bio-acoustic calibration issues, current test results may not match expected queues. See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for details.

## Frontend Integration

To use with the existing React frontend:

1. Start backend: `./start-backend.sh`
2. Start frontend: `./start-frontend.sh`
3. Frontend will be at: `http://localhost:5173`

### Mode 1: Call Log (Default)
View historical calls from `backend/data.py` with map visualization.

### Mode 2: Live Call Processing 🎙️
**NEW**: Real-time audio processing with microphone capture!

1. Click the **"🎙️ Live Call"** tab
2. Click **"▶ Start Live Call"**
3. Allow microphone access
4. Speak naturally - processing happens automatically on pauses
5. Watch transcript and triage update in real-time

**See [LIVE_PROCESSING_GUIDE.md](LIVE_PROCESSING_GUIDE.md) for detailed usage.**

### File Upload Processing

To integrate file upload analysis:

```javascript
// In React component
const analyzeCall = async (audioFile) => {
  const formData = new FormData();
  formData.append('file', audioFile);

  const response = await fetch('http://localhost:8000/api/analyze', {
    method: 'POST',
    body: formData
  });

  return await response.json();
};
```

## Production Deployment Checklist

Before deploying to production:

- [ ] Fix confidence scoring (use log-probabilities)
- [ ] Calibrate bio-acoustic thresholds with real data
- [ ] Add NLP layer (Ollama + Llama 3)
- [ ] Implement request queuing
- [ ] Add database persistence
- [ ] Set up monitoring/logging
- [ ] Model quantization for Raspberry Pi
- [ ] Security audit (input validation, rate limiting)
- [ ] Performance testing (load testing)
- [ ] Backup/disaster recovery

## Support

For issues or questions:
- See detailed status: [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
- Check API docs: `http://localhost:8000/docs`
- Review PRD: [../docs/TRIDENT_PRD.md](../docs/TRIDENT_PRD.md)
