# WebSocket Timing Fix

## Problem
After fixing the audio format issues, a new problem emerged:
```
ERROR:live_processor:Error sending update: Unexpected ASGI message 'websocket.send',
after sending 'websocket.close' or response already completed.
```

This occurred when the user disconnected before processing completed.

## Root Cause
When the WebSocket disconnects (user stops recording), the `finalize()` method still tries to:
1. Process remaining audio in buffer
2. Send processing updates through the closed WebSocket
3. Send final analysis

This causes "Unexpected ASGI message" errors because FastAPI prevents sending messages after the WebSocket is closed.

## Solution

### 1. Check WebSocket State Before Sending ([live_processor.py:347-360](backend/live_processor.py#L347-L360))

**Before**:
```python
async def send_update(self, data: Dict) -> None:
    try:
        await self.websocket.send_json(data)
    except Exception as e:
        logger.error(f"Error sending update: {e}")
```

**After**:
```python
async def send_update(self, data: Dict) -> None:
    try:
        # Check if WebSocket is still open
        if self.websocket.client_state.name == 'CONNECTED':
            await self.websocket.send_json(data)
    except Exception as e:
        # Silently ignore errors if WebSocket is closed
        logger.debug(f"Could not send update (WebSocket may be closed): {e}")
```

### 2. Track Session Active State ([live_processor.py:164](backend/live_processor.py#L164))

Added `is_active` flag to track if session is still active:
```python
def __init__(self, call_id: str, websocket: WebSocket):
    # ... existing code ...
    self.is_active = True  # Track if session is still active
```

### 3. Smart Finalization ([live_processor.py:375-410](backend/live_processor.py#L375-L410))

**Before**:
```python
async def finalize(self) -> Dict:
    # Always process remaining buffer
    if self.audio_buffer.get_duration() > 2.0:
        await self.process_buffer()  # ❌ Sends updates through closed WebSocket
```

**After**:
```python
async def finalize(self) -> Dict:
    # Mark session as inactive
    self.is_active = False

    # Only process if WebSocket still connected
    if self.audio_buffer.get_duration() > 2.0:
        try:
            if self.websocket.client_state.name == 'CONNECTED':
                await self.process_buffer()  # ✅ Only if WebSocket open
            else:
                logger.info("WebSocket closed, skipping final buffer processing")
        except Exception as e:
            logger.debug(f"Could not process final buffer: {e}")
```

## Behavior Changes

### When User Stays Connected Until End
1. ✅ All audio processed
2. ✅ All updates sent
3. ✅ Final analysis delivered
4. ✅ Clean shutdown

### When User Disconnects Early
1. ✅ WebSocket closes immediately
2. ✅ No errors trying to send through closed socket
3. ✅ Remaining buffer discarded (user left anyway)
4. ✅ Clean shutdown with partial results

## Testing

### Test Case 1: Normal Flow
1. Start live call
2. Speak for 10-15 seconds
3. Wait for processing to complete
4. Click "End Call"
5. **Expected**: All updates received, no errors

### Test Case 2: Early Disconnect
1. Start live call
2. Speak for 5 seconds
3. Immediately click "End Call" (while still recording)
4. **Expected**: No "Unexpected ASGI message" errors in logs

### Test Case 3: Long Processing
1. Start live call
2. Speak for 20+ seconds
3. Pause (trigger processing)
4. Disconnect during processing
5. **Expected**: Processing completes in background, no errors

## Log Output

### Before Fix
```
ERROR:live_processor:Error sending update: Unexpected ASGI message 'websocket.send'
ERROR:live_processor:Error sending update: Unexpected ASGI message 'websocket.send'
ERROR:live_processor:Error sending update: Unexpected ASGI message 'websocket.send'
```

### After Fix
```
INFO:live_processor:WebSocket disconnected: LIVE-0573E65F
INFO:live_processor:Finalizing call: LIVE-0573E65F
INFO:live_processor:WebSocket closed, skipping final buffer processing
INFO:live_processor:Call session ended: LIVE-0573E65F, Duration: 51.32s
```

## Files Modified

1. [`backend/live_processor.py`](backend/live_processor.py)
   - Line 164: Added `is_active` flag
   - Lines 347-360: Check WebSocket state before sending
   - Lines 375-410: Smart finalization with state checking

## Benefits

1. ✅ **No More Errors**: Clean handling of early disconnects
2. ✅ **Graceful Degradation**: Partial results if user disconnects
3. ✅ **Better Logging**: Debug vs error level messages
4. ✅ **Resource Efficient**: Skip processing if client is gone

## Summary

The WebSocket timing fix ensures clean shutdown regardless of when the user disconnects. The system now:
- Checks WebSocket state before sending
- Tracks session active state
- Skips processing if client disconnected
- Logs appropriately at debug level instead of error level
