# TRIDENT Quick Reference Card

## 🚀 Start System (2 Commands)

```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

Then open: `http://localhost:5173`

---

## 🎙️ Live Call Mode

1. Click **"🎙️ Live Call"** tab
2. Click **"▶ Start Live Call"**
3. **Speak** → **Pause 2s** → **See Results**

**Latency**: 7-12 seconds from speech to results

---

## 📋 Call Log Mode (Default)

- View historical calls
- Click calls on map
- See full analysis

---

## 🔧 Quick Checks

### Backend Running?
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","total_calls":X}
```

### Dependencies OK?
```bash
cd backend && python check_dependencies.py
```

### ffmpeg Installed?
```bash
ffmpeg -version
# macOS install: brew install ffmpeg
```

---

## 📊 Status Indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 CONNECTED | Ready to record |
| 🟡 CONNECTING | Establishing connection |
| 🔴 ERROR | Connection failed |
| ⚙️ Processing... | Analyzing audio |
| 🔴 ● RECORDING | Actively capturing |

---

## 🎯 Triage Queues

| Queue | Color | Priority | When? |
|-------|-------|----------|-------|
| Q1-IMMEDIATE | 🔴 Red | 1 | High distress + Low confidence |
| Q3-MONITOR | 🟡 Amber | 3 | High distress + High confidence |
| Q5-REVIEW | 🟢 Green | 5 | Low distress + Low confidence |
| Q5-ROUTINE | 🟢 Green | 5 | Low distress + High confidence |

---

## 🐛 Common Issues

### "EBML header" or "Format not recognised"
- **Status**: ✅ FIXED (switched to WAV format)
- **Check**: Browser console should show "Recording started with audio/wav codec"

### Connection Fails
- **Fix**: Backend not running → Start with `uvicorn main:app --reload`

### No Processing
- **Fix**: Speak clearly, pause 2+ seconds

### Empty Transcript
- **Fix**: Check mic permissions, speak louder

### Still seeing WebM errors?
- **Fix**: Hard refresh browser (Ctrl+Shift+R) to load new code

---

## 📁 Key Files

```
backend/
├── main.py              # API + WebSocket endpoint
├── live_processor.py    # Live processing logic
├── asr_service.py       # Whisper ASR
├── audio_processor.py   # Bio-acoustic
└── triage_engine.py     # Decision logic

frontend/src/
├── App.jsx              # Main app + mode toggle
├── components/
│   └── LiveCall.jsx     # Live call UI
└── hooks/
    ├── useAudioRecorder.js
    └── useWebSocket.js
```

---

## 🔗 API Endpoints

### REST
- `GET /api/calls` - Get all calls
- `GET /api/calls/{id}` - Get call by ID
- `POST /api/analyze` - Upload audio file
- `GET /health` - Health check

### WebSocket
- `ws://localhost:8000/ws/live` - Live audio stream

---

## 📞 Test Audio

```bash
# Test with sample file
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@assets/call_1_calm.wav"
```

---

## 🎤 Live Testing Script

**Say this** for demo:

> "Yes, I want to report a fallen power line on Main Street near the church.
> The line is down across the road and there are sparks.
> Traffic is backing up and it's getting dangerous."

**Expected**: Q3-MONITOR or Q5-ROUTINE depending on tone

---

## ⚡ Performance Tips

1. **First call**: 10-15s (model loading)
2. **Subsequent**: 5-10s (normal)
3. **Reduce latency**: Edit `live_processor.py` line 64: `silence_duration = 1.0`
4. **More responsive**: Edit `LiveCall.jsx` line 74: `chunkInterval: 500`

---

## 📚 Full Docs

- [QUICK_START.md](docs/QUICK_START.md)
- [LIVE_PROCESSING_GUIDE.md](docs/LIVE_PROCESSING_GUIDE.md)
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 💡 Pro Tips

- **First time**: Run `python check_dependencies.py`
- **Debugging**: Check browser console (F12) + backend logs
- **Better accuracy**: Speak clearly, good microphone
- **Faster VAD**: Pause 2+ seconds between sentences
- **Production**: Use HTTPS + WSS (not HTTP + WS)

---

**System Status**: ✅ READY
**Last Updated**: Dec 13, 2025
