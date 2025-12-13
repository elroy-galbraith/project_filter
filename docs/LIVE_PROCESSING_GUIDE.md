# TRIDENT Live Processing Guide

## Overview

TRIDENT now supports **real-time audio processing** for live emergency calls. This allows dispatchers to:
- Capture audio directly from their microphone via browser
- Stream audio to the TRIDENT backend in real-time
- Receive live transcription updates as the caller speaks
- Monitor bio-acoustic distress indicators in real-time
- See triage decisions update dynamically

## Architecture

### System Flow

```
┌─────────────────────────────────────────────────────────┐
│ Dispatcher's Browser                                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Live Call Component                               │  │
│  │ - MediaRecorder API (capture mic)                │  │
│  │ - WebSocket client (stream audio)                │  │
│  │ - Real-time UI updates                           │  │
│  └───────────────┬──────────────────────────────────┘  │
└──────────────────┼──────────────────────────────────────┘
                   │ WebSocket Connection
                   │ ws://localhost:8000/ws/live
                   │
┌──────────────────▼──────────────────────────────────────┐
│ Backend (FastAPI + WebSocket)                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Live Processor (/ws/live)                        │  │
│  │ - Audio buffering (1-second chunks)              │  │
│  │ - VAD-based utterance detection                  │  │
│  │ - Triggers processing on silence (1.5s)          │  │
│  └───────────────┬──────────────────────────────────┘  │
│                  │                                       │
│     ┌────────────┴───────────┐                          │
│     ▼                        ▼                          │
│  ┌─────────────┐      ┌──────────────┐                 │
│  │ ASR Service │      │ Bio-Acoustic │                 │
│  │ (Whisper)   │      │ Processor    │                 │
│  └──────┬──────┘      └──────┬───────┘                 │
│         │                    │                          │
│         └─────────┬──────────┘                          │
│                   ▼                                      │
│         ┌────────────────────┐                          │
│         │ Triage Engine      │                          │
│         └────────┬───────────┘                          │
│                  │                                       │
│                  ▼                                       │
│   WebSocket emit: JSON updates                          │
│   - transcript, confidence, bio_acoustic, triage        │
└──────────────────────────────────────────────────────────┘
```

### Key Features

1. **VAD-Based Processing**: Voice Activity Detection triggers processing when silence is detected (1.5 seconds of quiet)
2. **Incremental Updates**: Transcript and triage decisions update as new utterances are processed
3. **Low Latency**: ~5-10 seconds from speech to triage decision
4. **Browser-Based**: No special hardware required - works with any computer microphone

## Quick Start

### 0. Check Dependencies (First Time)

```bash
cd backend
source venv/bin/activate
python check_dependencies.py
```

This verifies:
- Python packages installed
- **ffmpeg installed** (required for WebM audio decoding)
- Whisper model ready
- GPU acceleration available
- Audio processing working

**Critical:** If ffmpeg is missing, install it:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

### 1. Start the Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

The WebSocket endpoint will be available at: `ws://localhost:8000/ws/live`

### 2. Start the Frontend

```bash
cd frontend
npm install  # if first time
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### 3. Use Live Processing

1. Open the frontend in your browser
2. Click the **"🎙️ Live Call"** tab in the mode toggle
3. Click **"▶ Start Live Call"**
4. Allow microphone access when prompted
5. Start speaking naturally
6. Watch the transcript and triage update live!
7. Click **"⏹ End Call"** when finished

## Usage Guide

### Starting a Live Call

When you click "Start Live Call":
1. WebSocket connection is established to backend
2. Browser requests microphone permission
3. MediaRecorder starts capturing audio in 1-second chunks
4. Each chunk is sent to backend via WebSocket
5. Backend accumulates chunks in audio buffer

### Processing Flow

**Audio Capture → Buffering → VAD → Processing → Results**

1. **Audio Capture**: Browser captures microphone audio at 16kHz (mono)
2. **Buffering**: Audio chunks accumulated in backend buffer
3. **VAD Trigger**: When 1.5 seconds of silence detected, processing begins
4. **Processing**:
   - ASR transcribes the utterance (~5-10 seconds)
   - Bio-acoustic analysis extracts vocal features (<1 second)
   - Triage engine determines priority queue
5. **Results**: Updates sent to browser via WebSocket

### UI Components

#### Status Indicators

- **Connection**: Shows WebSocket connection state (CONNECTED, CONNECTING, DISCONNECTED, ERROR)
- **Duration**: Total audio captured in seconds
- **Chunks**: Number of audio chunks sent
- **Processing**: Animated indicator when backend is processing

#### Live Results

- **Triage Status**: Color-coded priority queue with dispatcher guidance
  - 🔴 Q1-IMMEDIATE: Critical emergency (red glow)
  - 🟡 Q3-MONITOR: Elevated concern (amber)
  - 🟢 Q5-ROUTINE/REVIEW: Standard logging (green)

- **Live Transcript**: Real-time transcript updates with confidence score

- **Bio-Acoustic Meters**:
  - F0 Mean (pitch)
  - Distress Score (composite)
  - Energy level
  - Instability

## Technical Details

### Backend Components

#### 1. `live_processor.py`

**AudioBuffer Class**:
- Accumulates audio chunks
- Implements VAD using RMS energy threshold
- Triggers processing when silence detected or buffer full (30s max)

**LiveCallSession Class**:
- Manages single call session state
- Handles WebSocket communication
- Coordinates ASR, bio-acoustic, and triage processing
- Emits real-time updates to client

**Key Parameters**:
```python
sample_rate = 16000  # Hz (Whisper standard)
chunk_duration = 1.0  # seconds
energy_threshold = 0.01  # RMS for voice activity
silence_duration = 1.5  # seconds to trigger processing
```

#### 2. WebSocket Endpoint (`/ws/live`)

**Messages Sent to Client**:

```json
// Connection established
{
  "type": "connected",
  "call_id": "LIVE-A1B2C3D4",
  "message": "Live processing ready. Start speaking..."
}

// Buffer status update
{
  "type": "buffer_update",
  "duration": 2.5,
  "chunks_received": 3
}

// Processing started
{
  "type": "processing_started",
  "duration": 3.2
}

// Processing complete
{
  "type": "processing_complete",
  "transcript": "Full transcript so far...",
  "transcript_chunk": "Latest utterance only",
  "confidence": 0.85,
  "bio_acoustic": {
    "f0_mean": 185.3,
    "distress_score": 0.42,
    ...
  },
  "triage": {
    "queue": "Q5-ROUTINE",
    "priority_level": 5,
    "dispatcher_action": "...",
    ...
  },
  "call_duration": 15.7
}

// Error occurred
{
  "type": "error",
  "message": "Processing error: ..."
}

// Call ended
{
  "type": "call_ended",
  "analysis": {
    "call_id": "LIVE-A1B2C3D4",
    "duration": 45.2,
    "transcript": "Complete transcript",
    "confidence": 0.88,
    ...
  }
}
```

### Frontend Components

#### 1. `useAudioRecorder.js` Hook

Manages microphone capture using MediaRecorder API:

```javascript
const { startRecording, stopRecording, isRecording, error } = useAudioRecorder({
  onAudioChunk: (blob) => {
    // Callback when audio chunk ready
    ws.send(blob);
  },
  chunkInterval: 1000  // milliseconds
});
```

**Features**:
- Requests microphone permission
- Configures audio settings (16kHz, mono, echo cancellation)
- Emits audio chunks at specified interval
- Handles errors gracefully

#### 2. `useWebSocket.js` Hook

Manages WebSocket connection:

```javascript
const { connect, disconnect, sendAudio, connectionState } = useWebSocket({
  url: 'ws://localhost:8000/ws/live',
  onMessage: (data) => {
    // Handle server messages
    console.log(data.type, data);
  }
});
```

**Features**:
- Auto-reconnection on disconnect
- Binary data sending (audio chunks)
- JSON message parsing
- Connection state tracking

#### 3. `LiveCall.jsx` Component

Main live call UI component:
- Integrates audio recorder and WebSocket
- Displays live status and results
- Provides start/stop controls
- Shows instructions

## Performance Considerations

### Latency Breakdown

| Stage | Duration | Notes |
|-------|----------|-------|
| Audio capture | 1s | Chunk interval |
| VAD detection | 1.5s | Silence trigger |
| ASR transcription | 5-10s | Depends on utterance length |
| Bio-acoustic | <1s | Fast feature extraction |
| Triage | <0.1s | Simple decision logic |
| **Total** | **~7-12s** | From speech end to result |

### Optimization Tips

1. **Reduce Chunk Interval**: Lower to 500ms for faster VAD (but more overhead)
2. **Adjust Silence Duration**: Lower to 1.0s for faster triggering
3. **GPU Acceleration**: Ensure MPS (Mac) or CUDA (NVIDIA) enabled for Whisper
4. **Model Quantization**: Use INT8 quantized Whisper for faster inference

## Troubleshooting

### Microphone Access Issues

**Problem**: Browser doesn't request microphone permission

**Solution**:
- Ensure you're using HTTPS (or localhost for development)
- Check browser permissions: Settings → Privacy → Microphone
- Try different browser (Chrome/Firefox recommended)

### WebSocket Connection Fails

**Problem**: Connection state stuck on "CONNECTING" or shows "ERROR"

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health

# Check WebSocket endpoint
# Should return "Upgrade Required" error (normal for non-WS request)
curl -i http://localhost:8000/ws/live

# Verify CORS settings in backend/main.py
# Ensure your frontend URL is in allow_origins
```

### No Processing Happens

**Problem**: Audio chunks sent but no processing complete message

**Solution**:
1. Check backend logs for errors:
   ```bash
   # Look for "Processing buffer" messages
   tail -f backend_logs.txt
   ```

2. Verify audio quality:
   - Speak clearly and pause for 1.5+ seconds
   - Check if VAD threshold too high (try lowering energy_threshold)

3. Check model loading:
   - First call takes 10-15 seconds (model loading)
   - Subsequent calls should be faster

### High Latency

**Problem**: Results take >15 seconds to appear

**Solution**:
1. Check system resources:
   ```bash
   # Monitor CPU/RAM usage
   top
   ```

2. Verify GPU acceleration:
   ```bash
   # Check device in backend logs
   # Should show "Using device: mps" or "cuda"
   ```

3. Consider model quantization:
   - Use `faster-whisper` library
   - Apply INT8 quantization

## Browser Compatibility

| Browser | Supported | Notes |
|---------|-----------|-------|
| Chrome/Edge | ✅ Yes | Best performance |
| Firefox | ✅ Yes | Good support |
| Safari | ✅ Yes | May need permissions reset |
| Mobile browsers | ⚠️ Limited | WebSocket + MediaRecorder support varies |

## Security Considerations

### Production Deployment

For production use, implement:

1. **HTTPS/WSS**: Use secure WebSocket (wss://) connections
2. **Authentication**: Add token-based auth to WebSocket endpoint
3. **Rate Limiting**: Prevent abuse of processing resources
4. **Input Validation**: Validate audio format and size
5. **Session Timeout**: Auto-end calls after inactivity

Example secure WebSocket URL:
```javascript
wss://api.trident.example.com/ws/live?token=<auth_token>
```

## Comparison: Live vs Batch Processing

| Feature | Live Processing | Batch Processing |
|---------|----------------|------------------|
| **Use Case** | Real-time dispatcher demo | Post-call analysis |
| **Latency** | 7-12 seconds | Immediate (file already complete) |
| **Accuracy** | Same (Whisper Large V3) | Same |
| **Resource Usage** | Continuous | Burst on upload |
| **Best For** | Live demos, real-time triage | Production deployment, analysis |

## Future Enhancements

### Planned Features

1. **True Streaming ASR**: Replace Whisper with streaming-native model (Vosk, DeepSpeech)
2. **Multi-Speaker Diarization**: Identify caller vs dispatcher
3. **Live Waveform Visualization**: Show audio waveform in real-time
4. **Call Recording**: Save audio and transcript to database
5. **Dispatcher Annotations**: Add notes during live call

### Performance Improvements

1. **Parallel Processing**: Run ASR and bio-acoustic in parallel threads
2. **Model Caching**: Pre-load models on server start
3. **Edge Deployment**: Run on Raspberry Pi 5 for portable use

## Support

For issues or questions about live processing:
- Check logs: `backend/logs/` and browser console
- Review [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for known issues
- See main [QUICK_START.md](QUICK_START.md) for general TRIDENT usage

---

**Last Updated**: December 13, 2025
**Version**: 1.0 (PoC with Live Processing)
