from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import os
import tempfile
import logging
import uuid

from models import Call
from data import CALL_LOG
from audio_processor import BioAcousticProcessor
from asr_service import ASRService
from triage_engine import TriageEngine
from live_processor import handle_live_call

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TRIDENT API", version="1.0.0")

# Initialize TRIDENT processing services (lazy loading)
bio_processor = BioAcousticProcessor()
asr_service = ASRService()
triage_engine = TriageEngine()

# CORS middleware for local React dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Serve audio files from assets directory
assets_path = os.path.join(os.path.dirname(__file__), "..", "assets")
if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")


@app.get("/")
def root():
    return {
        "message": "TRIDENT API - Triage via Dual-stream Emergency Natural language and Tone",
        "docs": "/docs",
        "endpoints": {
            "calls": "/api/calls",
            "call_by_id": "/api/calls/{call_id}"
        }
    }


@app.get("/api/calls", response_model=List[Call])
def get_calls():
    """Get all calls in the system"""
    return CALL_LOG


@app.get("/api/calls/{call_id}", response_model=Call)
def get_call(call_id: str):
    """Get a specific call by ID"""
    for call in CALL_LOG:
        if call.id == call_id:
            return call
    raise HTTPException(status_code=404, detail=f"Call {call_id} not found")


@app.get("/health")
def health_check():
    return {"status": "healthy", "total_calls": len(CALL_LOG)}


@app.websocket("/ws/live")
async def websocket_live_call(websocket: WebSocket):
    """
    WebSocket endpoint for live audio processing.

    Client sends:
    - Binary audio chunks (WebM, WAV, or other format supported by librosa)

    Server sends (JSON):
    - {"type": "connected", "call_id": "...", "message": "..."}
    - {"type": "buffer_update", "duration": 1.5, "chunks_received": 3}
    - {"type": "processing_started", "duration": 2.5}
    - {"type": "processing_complete", "transcript": "...", "confidence": 0.85, ...}
    - {"type": "error", "message": "..."}
    - {"type": "call_ended", "analysis": {...}}

    Usage:
        const ws = new WebSocket('ws://localhost:8000/ws/live');
        ws.onopen = () => {
            // Send audio chunks as binary
            mediaRecorder.ondataavailable = (e) => {
                ws.send(e.data);
            };
        };
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            // Handle updates based on data.type
        };
    """
    # Generate unique call ID
    call_id = f"LIVE-{uuid.uuid4().hex[:8].upper()}"

    # Handle the live call
    await handle_live_call(websocket, call_id)


@app.post("/api/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze uploaded audio file through TRIDENT processing pipeline.

    Processes audio through three layers:
    1. Layer 1 (ASR): Caribbean-tuned speech recognition with confidence scoring
    2. Layer 3 (Bio-Acoustic): Vocal distress detection via pitch/energy analysis
    3. Triage: Priority queue routing based on confidence × distress matrix

    Args:
        file: Audio file (WAV, MP3, etc. - librosa handles most formats)

    Returns:
        Complete TRIDENT analysis:
        {
            "transcript": str,
            "confidence": float,
            "bio_acoustic": {
                "f0_mean": float,
                "f0_cv": float,
                "pitch_elevation": float,
                "instability": float,
                "energy": float,
                "jitter": float,
                "distress_score": float
            },
            "triage": {
                "queue": str,
                "priority_level": int,
                "flag_audio_review": bool,
                "reasoning": str,
                "dispatcher_action": str,
                "escalation_required": bool
            }
        }
    """
    temp_file_path = None

    try:
        # Validate file upload
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        logger.info(f"Received audio file: {file.filename}")

        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        logger.info(f"Processing audio: {temp_file_path}")

        # Layer 1: ASR with confidence scoring
        logger.info("Running ASR (Layer 1)...")
        asr_result = asr_service.transcribe_with_confidence(temp_file_path)

        # Layer 3: Bio-acoustic distress detection
        logger.info("Running bio-acoustic analysis (Layer 3)...")
        bio_result = bio_processor.extract_features(temp_file_path)

        # Triage decision
        logger.info("Generating triage decision...")
        triage_result = triage_engine.generate_dispatcher_guidance(
            confidence=asr_result["confidence"],
            distress_score=bio_result["distress_score"],
            transcript=asr_result["transcript"]
        )

        logger.info(f"Analysis complete: Queue={triage_result['queue']}, "
                   f"Confidence={asr_result['confidence']:.3f}, "
                   f"Distress={bio_result['distress_score']:.3f}")

        # Cleanup temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        # Return complete analysis
        return {
            "transcript": asr_result["transcript"],
            "confidence": asr_result["confidence"],
            "bio_acoustic": bio_result,
            "triage": triage_result
        }

    except Exception as e:
        logger.error(f"Error processing audio: {e}")

        # Cleanup on error
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )
