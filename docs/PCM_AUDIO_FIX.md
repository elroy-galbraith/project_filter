# PCM Audio Format Fix - Live Processing

## Problem
The live audio processing system was experiencing format recognition errors when trying to decode audio chunks from the browser:

```
soundfile.LibsndfileError: Error opening '/var/folders/.../tmp*.wav': Format not recognised.
audioread.exceptions.NoBackendError
```

### Root Cause
1. **Browser Limitation**: MediaRecorder API in browsers does not support `audio/wav` MIME type
2. **Incomplete WebM Chunks**: MediaRecorder defaults to WebM format, but individual chunks don't have complete container headers
3. **Decode Failure**: librosa/soundfile cannot decode incomplete WebM chunks as valid audio files

## Solution: Raw PCM Audio Streaming

Instead of relying on encoded audio formats (WAV/WebM), we now use **raw PCM audio data** via the Web Audio API.

### Architecture

```
Browser (Frontend)                    Backend (Python)
─────────────────                    ────────────────
Microphone
    ↓
AudioContext (16kHz)
    ↓
ScriptProcessor
    ↓
Float32 PCM samples                  numpy.frombuffer()
    ↓                                     ↓
WebSocket.send(ArrayBuffer) ────────> np.float32 array
                                          ↓
                                      Audio buffer
                                          ↓
                                      VAD → ASR → Triage
```

### Frontend Changes ([useAudioRecorder.js](frontend/src/hooks/useAudioRecorder.js))

**Before**: MediaRecorder with WAV/WebM format
```javascript
const mediaRecorder = new MediaRecorder(stream, {
  mimeType: 'audio/wav'  // Not actually supported!
});
```

**After**: Web Audio API with raw PCM
```javascript
const audioContext = new AudioContext({ sampleRate: 16000 });
const processor = audioContext.createScriptProcessor(4096, 1, 1);

processor.onaudioprocess = (event) => {
  const audioChunk = new Float32Array(event.inputBuffer.getChannelData(0));
  // Send Float32 samples directly
  ws.send(audioChunk.buffer);
};
```

### Backend Changes ([live_processor.py](backend/live_processor.py))

**Before**: Decode WAV/WebM files
```python
# Save to temp file
with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
    tmp.write(audio_data)
    audio, _ = librosa.load(tmp.name)  # ❌ Fails on WebM chunks
```

**After**: Direct numpy conversion
```python
# Convert Float32 PCM bytes to numpy array
audio = np.frombuffer(audio_data, dtype=np.float32)
# ✅ Reliable, no file I/O, no format issues
```

## Benefits

1. **No Format Issues**: Raw PCM data has no container format to decode
2. **No File I/O**: Direct byte-to-numpy conversion (faster, cleaner)
3. **Reliable**: Float32 PCM is the native format browsers use internally
4. **Efficient**: No encoding/decoding overhead
5. **Cross-browser**: Web Audio API is universally supported

## Audio Specifications

- **Sample Rate**: 16 kHz (optimal for speech recognition)
- **Channels**: 1 (mono)
- **Format**: Float32 PCM (range: -1.0 to 1.0)
- **Chunk Size**: ~256ms (4096 samples at 16kHz)
- **Streaming Interval**: 1 second batches sent to backend

## Testing Checklist

- [ ] Start live call session
- [ ] Verify WebSocket connection
- [ ] Record audio and speak
- [ ] Confirm no format errors in logs
- [ ] Verify VAD triggers on silence
- [ ] Check ASR transcription appears
- [ ] Validate bio-acoustic features extracted
- [ ] Confirm triage decision updates
- [ ] Test call finalization

## Notes

- ScriptProcessor is deprecated but still widely supported. For production, consider migrating to AudioWorklet (requires separate worker file)
- Float32 PCM is sent in little-endian byte order (default for TypedArrays)
- Each 1-second chunk at 16kHz = 16,000 samples × 4 bytes = 64KB of data

## Files Modified

1. [frontend/src/hooks/useAudioRecorder.js](frontend/src/hooks/useAudioRecorder.js) - Web Audio API implementation
2. [backend/live_processor.py](backend/live_processor.py#L70-L101) - PCM decoding in AudioBuffer.add_chunk()
