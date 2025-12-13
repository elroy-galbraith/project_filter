# Audio Format Fix - Summary

## Problem Fixed
The live audio processing system was failing with `Format not recognised` errors when trying to decode audio chunks from the browser.

## Root Cause
MediaRecorder API in browsers doesn't support `audio/wav` MIME type, and WebM chunks sent by MediaRecorder don't have complete container headers, making them undecodable by librosa/soundfile.

## Solution Implemented
Switched from encoded audio formats (WAV/WebM) to **raw PCM audio streaming** using the Web Audio API.

## Changes Made

### 1. Frontend - [useAudioRecorder.js](frontend/src/hooks/useAudioRecorder.js)
**Changed from**: MediaRecorder with WAV/WebM encoding
**Changed to**: Web Audio API with raw Float32 PCM samples

**Key changes**:
- Use `AudioContext` with 16kHz sample rate
- Use `ScriptProcessor` to capture raw audio samples
- Send Float32 PCM ArrayBuffer via WebSocket (no encoding)
- Collect samples every 1 second and send in batches

### 2. Backend - [live_processor.py](backend/live_processor.py#L70-L101)
**Changed from**: File-based WAV/WebM decoding with librosa
**Changed to**: Direct numpy array conversion from PCM bytes

**Key changes**:
- Use `np.frombuffer(audio_data, dtype=np.float32)` to convert bytes to audio
- No temporary file creation needed
- No format decoding required
- Direct buffer concatenation for audio accumulation

### 3. Frontend - [LiveCall.jsx](frontend/src/components/LiveCall.jsx#L95-L97)
**Updated**: Documentation to reflect ArrayBuffer instead of Blob

## Technical Specifications

| Property | Value |
|----------|-------|
| Sample Rate | 16 kHz |
| Channels | 1 (mono) |
| Format | Float32 PCM |
| Value Range | -1.0 to 1.0 |
| Chunk Size | ~4096 samples (~256ms) |
| Send Interval | 1 second batches |
| Data Size | ~64KB per second |

## Benefits

1. ✅ **No format errors** - Raw PCM has no container format to decode
2. ✅ **No file I/O** - Direct byte-to-numpy conversion (faster, cleaner)
3. ✅ **Reliable** - Float32 PCM is the native browser format
4. ✅ **Efficient** - No encoding/decoding overhead
5. ✅ **Cross-browser** - Web Audio API is universally supported

## Testing

To test the fix:

1. Start the backend server:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload
   ```

2. Start the frontend dev server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open the app and navigate to Live Call
4. Click "Start Live Call" and allow microphone access
5. Speak into the microphone
6. Verify:
   - No format errors in backend logs
   - Buffer updates appear in UI
   - VAD triggers on silence (~1.5s pause)
   - Transcript appears after processing
   - Bio-acoustic features display
   - Triage decision updates

## Files Modified

1. [`frontend/src/hooks/useAudioRecorder.js`](frontend/src/hooks/useAudioRecorder.js) - Web Audio API implementation
2. [`backend/live_processor.py`](backend/live_processor.py) - PCM decoding
3. [`frontend/src/components/LiveCall.jsx`](frontend/src/components/LiveCall.jsx) - Documentation update

## Documentation Created

1. [`PCM_AUDIO_FIX.md`](PCM_AUDIO_FIX.md) - Detailed technical documentation
2. [`AUDIO_FIX_SUMMARY.md`](AUDIO_FIX_SUMMARY.md) - This file

## Next Steps

The system is now ready for testing. The audio pipeline should work reliably without format recognition errors.

If you encounter issues:
1. Check browser console for JavaScript errors
2. Check backend logs for Python errors
3. Verify microphone permissions are granted
4. Ensure WebSocket connection is established (watch for "WebSocket connected" message)

## Notes

- `ScriptProcessor` is deprecated but still widely supported
- For production, consider migrating to `AudioWorklet` (requires separate worker file)
- Float32 PCM is sent in little-endian byte order (JavaScript TypedArray default)
