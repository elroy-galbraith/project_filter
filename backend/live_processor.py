"""
TRIDENT Live Audio Processing Module

Implements WebSocket-based real-time audio streaming with incremental
ASR transcription, bio-acoustic analysis, and live triage updates.

Architecture:
- WebSocket endpoint receives audio chunks from browser
- VAD-based buffering accumulates until utterance complete
- Incremental processing emits updates as audio arrives
- Live triage decision updates in real-time

Key Features:
- Voice Activity Detection (VAD) for utterance boundary detection
- Sliding window bio-acoustic analysis
- Incremental confidence and distress scoring
- WebSocket event emission for real-time UI updates
"""

import asyncio
import io
import logging
import numpy as np
import librosa
from typing import Dict, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import json

from asr_service import ASRService
from audio_processor import BioAcousticProcessor
from triage_engine import TriageEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioBuffer:
    """
    Manages audio buffering for streaming processing.

    Accumulates audio chunks and provides utilities for
    VAD-based utterance detection and processing.
    """

    def __init__(self, sample_rate: int = 16000, chunk_duration: float = 1.0):
        """
        Initialize audio buffer.

        Args:
            sample_rate: Audio sample rate in Hz
            chunk_duration: Duration of each processing chunk in seconds
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)

        # Audio buffer
        self.buffer = np.array([], dtype=np.float32)
        self.total_duration = 0.0

        # VAD parameters
        self.energy_threshold = 0.01  # RMS energy threshold for voice activity
        self.silence_duration = 1.5  # Seconds of silence to trigger processing
        self.last_voice_time = 0.0

    def add_chunk(self, audio_data: bytes) -> None:
        """
        Add audio chunk to buffer.

        Args:
            audio_data: Raw PCM audio bytes (Float32 format from Web Audio API)
        """
        if len(audio_data) == 0:
            logger.warning("Received empty audio chunk, skipping")
            return

        try:
            # Convert bytes to numpy array (Float32 PCM)
            # Web Audio API sends Float32 samples in range [-1.0, 1.0]
            audio = np.frombuffer(audio_data, dtype=np.float32)

            if len(audio) > 0:
                # Append to buffer
                self.buffer = np.concatenate([self.buffer, audio])
                self.total_duration = len(self.buffer) / self.sample_rate

                # Update voice activity
                rms = np.sqrt(np.mean(audio**2))
                if rms > self.energy_threshold:
                    self.last_voice_time = self.total_duration

                logger.debug(f"Buffer updated: {self.total_duration:.1f}s total, RMS={rms:.4f}")

        except Exception as e:
            logger.error(f"Error adding audio chunk: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def should_process(self) -> bool:
        """
        Determine if buffer should be processed based on VAD.

        Returns:
            True if silence detected or buffer full, False otherwise
        """
        if len(self.buffer) == 0:
            return False

        # Process if we have silence after voice activity
        silence_duration = self.total_duration - self.last_voice_time

        if silence_duration >= self.silence_duration and self.last_voice_time > 0:
            logger.info(f"VAD trigger: {silence_duration:.2f}s silence detected")
            return True

        # Process if buffer exceeds 30 seconds (fallback)
        if self.total_duration >= 30.0:
            logger.info(f"Buffer overflow: {self.total_duration:.2f}s, forcing process")
            return True

        return False

    def get_audio(self) -> np.ndarray:
        """
        Get current audio buffer.

        Returns:
            Audio samples as numpy array
        """
        return self.buffer.copy()

    def clear(self) -> None:
        """Clear the audio buffer."""
        self.buffer = np.array([], dtype=np.float32)
        self.total_duration = 0.0
        self.last_voice_time = 0.0
        logger.debug("Buffer cleared")

    def get_duration(self) -> float:
        """Get current buffer duration in seconds."""
        return self.total_duration


class LiveCallSession:
    """
    Manages a single live call processing session.

    Handles audio buffering, incremental processing, and
    WebSocket communication for real-time updates.
    """

    def __init__(
        self,
        call_id: str,
        websocket: WebSocket,
        asr_service=None,
        bio_processor=None,
        triage_engine=None
    ):
        """
        Initialize live call session.

        Args:
            call_id: Unique identifier for the call
            websocket: WebSocket connection for this session
            asr_service: Shared ASR service instance (optional)
            bio_processor: Shared bio-acoustic processor instance (optional)
            triage_engine: Shared triage engine instance (optional)
        """
        self.call_id = call_id
        self.websocket = websocket
        self.start_time = datetime.now()
        self.is_active = True  # Track if session is still active

        # Audio buffer
        self.audio_buffer = AudioBuffer(sample_rate=16000, chunk_duration=1.0)

        # Processing services (shared singletons from main.py)
        self.asr_service = asr_service
        self.bio_processor = bio_processor
        self.triage_engine = triage_engine

        # Session state
        self.full_transcript = ""
        self.latest_confidence = 0.0
        self.latest_distress = 0.0
        self.current_triage = None
        self.chunk_count = 0

        logger.info(f"Live call session started: {call_id}")

    def _ensure_services_loaded(self):
        """Lazy load processing services on first use (fallback if not provided)."""
        if self.asr_service is None:
            logger.info("Loading processing services (fallback - services not injected)...")
            from asr_service import ASRService
            from audio_processor import BioAcousticProcessor
            from triage_engine import TriageEngine

            self.asr_service = ASRService()
            self.bio_processor = BioAcousticProcessor()
            self.triage_engine = TriageEngine()
            logger.info("Services loaded successfully")

    async def process_audio_chunk(self, audio_data: bytes) -> None:
        """
        Process incoming audio chunk.

        Args:
            audio_data: Raw audio bytes from WebSocket
        """
        try:
            # Add to buffer
            self.audio_buffer.add_chunk(audio_data)
            self.chunk_count += 1

            # Send buffer status update
            await self.send_update({
                "type": "buffer_update",
                "duration": self.audio_buffer.get_duration(),
                "chunks_received": self.chunk_count
            })

            # Check if we should process (VAD trigger)
            if self.audio_buffer.should_process():
                await self.process_buffer()

        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
            await self.send_error(f"Processing error: {str(e)}")

    async def process_buffer(self) -> None:
        """
        Process accumulated audio buffer with ASR + bio-acoustic + triage.
        """
        try:
            logger.info(f"Processing buffer: {self.audio_buffer.get_duration():.2f}s")

            # Ensure services are loaded
            self._ensure_services_loaded()

            # Get audio from buffer
            audio = self.audio_buffer.get_audio()

            if len(audio) == 0:
                logger.warning("Empty buffer, skipping processing")
                return

            # Send processing status
            await self.send_update({
                "type": "processing_started",
                "duration": len(audio) / 16000
            })

            # Run ASR and bio-acoustic in parallel
            # Note: Since these are CPU-intensive, we run them sequentially
            # For production, consider using asyncio.to_thread() or separate workers

            # 1. ASR Transcription
            logger.info("Running ASR...")
            asr_result = await asyncio.to_thread(
                self._transcribe_audio, audio
            )

            # Update transcript (append new text)
            if asr_result["transcript"]:
                if self.full_transcript:
                    self.full_transcript += " " + asr_result["transcript"]
                else:
                    self.full_transcript = asr_result["transcript"]
                self.latest_confidence = asr_result["confidence"]

            # 2. Bio-Acoustic Analysis
            logger.info("Running bio-acoustic analysis...")
            bio_result = await asyncio.to_thread(
                self._analyze_bio_acoustic, audio
            )
            self.latest_distress = bio_result["distress_score"]

            # 3. Triage Decision
            logger.info("Generating triage decision...")
            triage_result = self.triage_engine.generate_dispatcher_guidance(
                confidence=self.latest_confidence,
                distress_score=self.latest_distress,
                transcript=self.full_transcript
            )
            self.current_triage = triage_result

            # Send complete update
            await self.send_update({
                "type": "processing_complete",
                "transcript": self.full_transcript,
                "transcript_chunk": asr_result["transcript"],
                "confidence": self.latest_confidence,
                "bio_acoustic": bio_result,
                "triage": triage_result,
                "call_duration": self.audio_buffer.get_duration()
            })

            logger.info(f"Processing complete: Queue={triage_result['queue']}, "
                       f"Confidence={self.latest_confidence:.3f}, "
                       f"Distress={self.latest_distress:.3f}")

            # Clear buffer for next utterance
            self.audio_buffer.clear()

        except Exception as e:
            logger.error(f"Error processing buffer: {e}")
            import traceback
            traceback.print_exc()
            await self.send_error(f"Processing error: {str(e)}")

    def _transcribe_audio(self, audio: np.ndarray) -> Dict:
        """
        Transcribe audio using ASR service.

        Args:
            audio: Audio samples (numpy array)

        Returns:
            Dictionary with transcript and confidence
        """
        # Save to temporary WAV for ASR processing
        import tempfile
        import soundfile as sf

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            sf.write(tmp_file.name, audio, 16000)
            result = self.asr_service.transcribe_with_confidence(tmp_file.name)

            # Clean up
            import os
            os.unlink(tmp_file.name)

        return result

    def _analyze_bio_acoustic(self, audio: np.ndarray) -> Dict:
        """
        Analyze bio-acoustic features.

        Args:
            audio: Audio samples (numpy array)

        Returns:
            Dictionary with bio-acoustic features
        """
        # Save to temporary WAV for bio-acoustic processing
        import tempfile
        import soundfile as sf

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            sf.write(tmp_file.name, audio, 16000)
            result = self.bio_processor.extract_features(tmp_file.name)

            # Clean up
            import os
            os.unlink(tmp_file.name)

        return result

    async def send_update(self, data: Dict) -> None:
        """
        Send update to WebSocket client.

        Args:
            data: Update data to send
        """
        try:
            # Check if WebSocket is still open
            if self.websocket.client_state.name == 'CONNECTED':
                await self.websocket.send_json(data)
        except Exception as e:
            # Silently ignore errors if WebSocket is closed
            logger.debug(f"Could not send update (WebSocket may be closed): {e}")

    async def send_error(self, message: str) -> None:
        """
        Send error message to client.

        Args:
            message: Error message
        """
        await self.send_update({
            "type": "error",
            "message": message
        })

    async def finalize(self) -> Dict:
        """
        Finalize the call and return complete analysis.

        Saves call record to database for persistent storage.

        Returns:
            Complete call analysis
        """
        logger.info(f"Finalizing call: {self.call_id}")

        # Mark session as inactive
        self.is_active = False

        # Process any remaining audio in buffer (if significant and WebSocket still open)
        if self.audio_buffer.get_duration() > 2.0:  # Only process if >2s remaining
            # Check if WebSocket is still connected before processing
            try:
                if self.websocket.client_state.name == 'CONNECTED':
                    await self.process_buffer()
                else:
                    logger.info("WebSocket closed, skipping final buffer processing")
            except Exception as e:
                logger.debug(f"Could not process final buffer: {e}")

        # Calculate call duration
        end_time = datetime.now()
        call_duration = (end_time - self.start_time).total_seconds()

        # Save to database
        self._save_to_database(end_time, call_duration)

        # Return final analysis
        return {
            "call_id": self.call_id,
            "duration": call_duration,
            "transcript": self.full_transcript,
            "confidence": self.latest_confidence,
            "distress_score": self.latest_distress,
            "triage": self.current_triage,
            "chunks_processed": self.chunk_count
        }

    def _save_to_database(self, end_time: datetime, call_duration: float) -> None:
        """
        Save call record to database.

        Args:
            end_time: Call end timestamp
            call_duration: Total call duration in seconds
        """
        try:
            from database import SessionLocal, LiveCall

            db = SessionLocal()
            try:
                # Extract bio-acoustic features if available
                pitch_mean = None
                pitch_cv = None
                energy_rms = None
                jitter = None

                # Extract triage details
                triage_queue = None
                priority_level = None
                flag_audio_review = False
                escalation_required = False
                dispatcher_action = None
                triage_reasoning = None

                if self.current_triage:
                    triage_queue = self.current_triage.get("queue")
                    priority_level = self.current_triage.get("priority_level")
                    flag_audio_review = self.current_triage.get("flag_audio_review", False)
                    escalation_required = self.current_triage.get("escalation_required", False)
                    dispatcher_action = self.current_triage.get("dispatcher_action")
                    triage_reasoning = self.current_triage.get("reasoning")

                # Create database record
                live_call = LiveCall(
                    call_id=self.call_id,
                    start_time=self.start_time,
                    end_time=end_time,
                    duration_seconds=call_duration,
                    chunks_processed=self.chunk_count,
                    total_audio_duration=self.audio_buffer.total_duration,
                    transcript=self.full_transcript,
                    confidence_score=self.latest_confidence,
                    distress_score=self.latest_distress,
                    pitch_mean_hz=pitch_mean,
                    pitch_cv=pitch_cv,
                    energy_rms=energy_rms,
                    jitter=jitter,
                    triage_queue=triage_queue,
                    priority_level=priority_level,
                    flag_audio_review=flag_audio_review,
                    escalation_required=escalation_required,
                    dispatcher_action=dispatcher_action,
                    triage_reasoning=triage_reasoning,
                    triage_data=self.current_triage,
                    status="completed"
                )

                db.add(live_call)
                db.commit()
                db.refresh(live_call)

                logger.info(f"Call {self.call_id} saved to database (ID: {live_call.id})")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error saving call to database: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - database failure shouldn't crash the session


async def handle_live_call(
    websocket: WebSocket,
    call_id: str,
    asr_service=None,
    bio_processor=None,
    triage_engine=None
) -> None:
    """
    WebSocket handler for live call processing.

    Args:
        websocket: WebSocket connection
        call_id: Unique identifier for the call
        asr_service: Shared ASR service instance (optional)
        bio_processor: Shared bio-acoustic processor instance (optional)
        triage_engine: Shared triage engine instance (optional)
    """
    # Accept WebSocket connection
    await websocket.accept()
    logger.info(f"WebSocket connected: {call_id}")

    # Create session with shared services (preloaded at startup)
    session = LiveCallSession(
        call_id,
        websocket,
        asr_service=asr_service,
        bio_processor=bio_processor,
        triage_engine=triage_engine
    )

    try:
        # Send connection confirmation
        await session.send_update({
            "type": "connected",
            "call_id": call_id,
            "message": "Live processing ready. Start speaking..."
        })

        # Process incoming audio chunks
        while True:
            try:
                # Receive audio chunk (binary data)
                data = await websocket.receive_bytes()

                if len(data) == 0:
                    logger.warning("Received empty audio chunk")
                    continue

                # Process the chunk
                await session.process_audio_chunk(data)

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {call_id}")
                break

            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                await session.send_error(str(e))

    finally:
        # Finalize call
        final_analysis = await session.finalize()

        # Send final analysis (only if websocket still open)
        try:
            await session.send_update({
                "type": "call_ended",
                "analysis": final_analysis
            })
        except Exception as e:
            logger.debug(f"Could not send final update (connection already closed): {e}")

        logger.info(f"Call session ended: {call_id}, Duration: {final_analysis['duration']:.2f}s")
