# TRIDENT Troubleshooting Guide

## Quick Dependency Check

Before troubleshooting, run the dependency checker:

```bash
cd backend
source venv/bin/activate
python check_dependencies.py
```

This will verify all critical dependencies are installed.

---

## Live Processing Issues

### Error: "Format not recognised" when processing audio

**Symptoms:**
```
ERROR:live_processor:Error adding audio chunk: Error opening <_io.BytesIO object>: Format not recognised.
```

**Cause:** Missing ffmpeg or librosa can't decode WebM/Opus audio from browser

**Solution:**

1. **Install ffmpeg**:
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

2. **Verify installation**:
   ```bash
   ffmpeg -version
   ```

3. **Restart backend**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

---

### WebSocket Connection Fails

**Symptoms:**
- Connection state stuck on "CONNECTING"
- Console error: "WebSocket connection failed"

**Solutions:**

1. **Check backend is running**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy","total_calls":N}
   ```

2. **Check WebSocket endpoint**:
   ```bash
   # This should fail with "Upgrade Required" (normal for HTTP request to WS endpoint)
   curl -i http://localhost:8000/ws/live
   ```

3. **Verify CORS settings** in `backend/main.py`:
   ```python
   allow_origins=["http://localhost:5173", "http://localhost:3000", ...]
   ```

4. **Check firewall**:
   - Ensure port 8000 is not blocked
   - Try: `lsof -i :8000` to see if backend is listening

---

### Microphone Access Denied

**Symptoms:**
- Browser doesn't request permission
- Error: "Failed to access microphone"

**Solutions:**

1. **Browser Permissions**:
   - Chrome: Settings → Privacy → Site Settings → Microphone
   - Firefox: Preferences → Privacy & Security → Permissions → Microphone
   - Safari: Safari → Settings → Websites → Microphone

2. **HTTPS Requirement**:
   - Microphone access requires HTTPS (except localhost)
   - For development, use `http://localhost:5173` (works)
   - For production, use `https://your-domain.com`

3. **Reset Permissions**:
   - Chrome: Click lock icon in address bar → Reset permissions
   - Try in incognito/private mode

---

### No Processing Happens (Audio Sent But No Results)

**Symptoms:**
- Chunks sent (count increases)
- Duration increases
- But no "Processing..." or results appear

**Causes & Solutions:**

1. **VAD Not Triggering**:
   - **Cause**: Speaking too quietly or no silence pause
   - **Solution**: Speak clearly, pause for 2+ seconds
   - **Debug**: Check backend logs for "VAD trigger" or "Buffer overflow"

2. **Adjust VAD Sensitivity** in `backend/live_processor.py`:
   ```python
   # Line 63-64
   self.energy_threshold = 0.005  # Lower = more sensitive (try 0.005 instead of 0.01)
   self.silence_duration = 1.0    # Lower = faster trigger (try 1.0 instead of 1.5)
   ```

3. **Check Backend Logs**:
   ```bash
   # Look for "Processing buffer" messages
   tail -f logs.txt
   ```

4. **Model Loading**:
   - First call takes 10-15 seconds (model loading)
   - Check logs for "Loading Whisper base model"
   - Subsequent calls should be faster

---

### High Latency (>15 seconds to results)

**Symptoms:**
- Results take very long to appear
- "Processing..." shows for >15 seconds

**Solutions:**

1. **Check System Resources**:
   ```bash
   # Monitor CPU/RAM
   top

   # Check if Whisper model loaded
   ps aux | grep python
   ```

2. **Verify GPU Acceleration**:
   ```bash
   cd backend
   source venv/bin/activate
   python -c "import torch; print('MPS:', torch.backends.mps.is_available(), 'CUDA:', torch.cuda.is_available())"
   ```

3. **Optimize VAD Settings**:
   - Reduce `silence_duration` to 1.0s for faster triggering
   - Reduce `chunk_interval` to 500ms in frontend (more responsive)

4. **Model Quantization** (advanced):
   - Use `faster-whisper` library for INT8 quantization
   - 2-3x speed improvement

---

### Browser Console Errors

#### "Failed to construct 'MediaRecorder': The MediaRecorder cannot be created"

**Cause:** Unsupported codec

**Solution:**
- Check `useAudioRecorder.js` line 47-53
- Browser will auto-fallback to supported codec
- Verify in console: "Recording started with X codec"

#### "WebSocket error" with no details

**Solutions:**
1. Check backend console for errors
2. Verify WebSocket URL: `ws://localhost:8000/ws/live` (not `http://`)
3. Test WebSocket manually:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/live');
   ws.onopen = () => console.log('Connected');
   ws.onerror = (e) => console.error('Error', e);
   ```

---

### Empty or Garbled Transcripts

**Symptoms:**
- Transcript shows "..." or "[ERROR: Transcription failed]"
- Or transcript is nonsense

**Causes & Solutions:**

1. **Audio Quality**:
   - Speak clearly into microphone
   - Check microphone settings (not muted, correct input device)
   - Test with: `navigator.mediaDevices.enumerateDevices()`

2. **Model Issues**:
   - Check if LoRA adapter loaded correctly
   - Look for "LoRA adapter loaded successfully" in logs
   - If not found, it falls back to base model (still works)

3. **Audio Format**:
   - Browser should send WebM/Opus (check network tab)
   - Verify ffmpeg can decode: `ffmpeg -i test.webm -f null -`

---

### Bio-Acoustic Metrics Show Zero

**Symptoms:**
- F0 Mean: 0.0 Hz
- Distress Score: 0.0%

**Causes:**
1. **Silent Audio**: No voiced speech detected
2. **Processing Error**: Check logs for "No voiced frames detected"

**Solutions:**
- Speak louder and clearer
- Check microphone volume in system settings
- Ensure you're speaking, not typing/clicking

---

## Batch Processing Issues (File Upload)

### Model Loading Errors

**Error:** "LoRA adapter not found"

**Solution:**
```bash
# Check if model files exist
ls -la backend/model_full/

# Should see:
# - adapter_model.safetensors
# - adapter_config.json
# - tokenizer files
```

If missing, the system will use base Whisper (still works, just no Caribbean tuning).

---

### Memory Errors

**Error:** "RuntimeError: CUDA out of memory" or similar

**Solutions:**
1. Close other applications
2. Restart Python process
3. Use CPU instead (slower):
   ```python
   # In asr_service.py, force CPU
   self.device = "cpu"
   ```

---

## Development Issues

### Backend Won't Start

**Error:** "Address already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn main:app --reload --port 8001
```

---

### Frontend Won't Start

**Error:** "EADDRINUSE: address already in use"

**Solution:**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 5174
```

---

### Import Errors

**Error:** "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Or install missing package
pip install <package-name>
```

---

## Production Deployment Issues

### WebSocket Over HTTPS

**Issue:** WebSocket fails with `wss://` in production

**Solution:**
1. Ensure backend supports WSS (use reverse proxy like nginx)
2. Configure SSL certificates
3. Update frontend to use `wss://` instead of `ws://`

Example nginx config:
```nginx
location /ws/ {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## Performance Optimization

### Reduce Latency

1. **Adjust VAD Settings**:
   ```python
   # backend/live_processor.py
   silence_duration = 1.0  # Down from 1.5s
   energy_threshold = 0.005  # More sensitive
   ```

2. **Reduce Chunk Interval**:
   ```javascript
   // frontend/src/components/LiveCall.jsx
   chunkInterval: 500  // Down from 1000ms
   ```

3. **Parallel Processing**:
   ```python
   # Use asyncio.to_thread() for ASR and bio-acoustic
   asr_task = asyncio.create_task(asyncio.to_thread(self._transcribe_audio, audio))
   bio_task = asyncio.create_task(asyncio.to_thread(self._analyze_bio_acoustic, audio))

   asr_result = await asr_task
   bio_result = await bio_task
   ```

---

## Getting Help

If you're still stuck:

1. **Check Logs**:
   - Backend: Console output or log file
   - Frontend: Browser console (F12)

2. **Run Dependency Checker**:
   ```bash
   python backend/check_dependencies.py
   ```

3. **Test Components Individually**:
   ```bash
   # Test ASR
   python backend/asr_service.py ../assets/call_1_calm.wav

   # Test bio-acoustic
   python backend/audio_processor.py ../assets/call_1_calm.wav

   # Test pipeline
   python backend/test_pipeline.py
   ```

4. **Review Documentation**:
   - [QUICK_START.md](QUICK_START.md)
   - [LIVE_PROCESSING_GUIDE.md](LIVE_PROCESSING_GUIDE.md)
   - [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)

---

**Last Updated:** December 13, 2025
