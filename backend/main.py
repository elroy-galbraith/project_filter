from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy.orm import Session
import os
import tempfile
import logging
import uuid

from models import Call
from data import CALL_LOG
from audio_processor import BioAcousticProcessor
from asr_service import ASRService
from nlp_service import NLPService
from triage_engine import TriageEngine
from live_processor import handle_live_call
from database import init_db, get_db, LiveCall

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TRIDENT API", version="1.0.0")

# Initialize database and preload models on startup
@app.on_event("startup")
def startup_event():
    """Initialize database and preload ML models on application startup."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

    # Preload ASR model to avoid cold start latency
    logger.info("Preloading ASR model (Whisper + LoRA)...")
    try:
        asr_service._load_models()
        logger.info("ASR model preloaded successfully")
    except Exception as e:
        logger.error(f"Failed to preload ASR model: {e}")
        logger.warning("ASR model will be loaded on first request (lazy loading)")

    logger.info("TRIDENT backend ready")

# Initialize TRIDENT processing services (lazy loading)
bio_processor = BioAcousticProcessor()
asr_service = ASRService()
nlp_service = NLPService()
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
def get_calls(db: Session = Depends(get_db)):
    """
    Get all calls in the system (both mock data and live calls).

    Combines:
    - Mock calls from CALL_LOG (demo data)
    - Live calls from database (real WebSocket sessions)

    Returns calls in unified format for map visualization.
    """
    # Start with mock calls
    all_calls = list(CALL_LOG)

    # Add live calls from database
    live_calls = db.query(LiveCall).all()

    for live_call in live_calls:
        # Convert LiveCall to Call format for UI compatibility
        call_dict = {
            "id": live_call.call_id,
            "time": live_call.start_time.strftime("%H:%M:%S") if live_call.start_time else "N/A",
            "audio_file": "",  # Live calls don't have audio files (yet)
            "transcript": live_call.transcript or "",
            "confidence": live_call.confidence_score or 0.0,
            "pitch_avg": int(live_call.pitch_mean_hz) if live_call.pitch_mean_hz else 150,
            "energy_avg": live_call.energy_rms or 0.0,
            "distress_score": int(live_call.distress_score or 0),
            "is_distress": (live_call.distress_score or 0) > 50,
            "status": live_call.triage_queue or "LIVE-PROCESSED",
            "location": live_call.location or "Jamaica (Location not specified)",
            "category": live_call.category or "EMERGENCY CALL",
            "lat": live_call.lat or 18.1096,  # Default to Jamaica center
            "lng": live_call.lng or -77.2975,
            "nlp_extraction": None  # Could be added in future
        }

        all_calls.append(Call(**call_dict))

    return all_calls


@app.get("/api/calls/{call_id}", response_model=Call)
def get_call(call_id: str, db: Session = Depends(get_db)):
    """
    Get a specific call by ID (supports both mock and live calls).

    Args:
        call_id: Call ID (e.g., "CALL-1042" for mock, "LIVE-ABC123" for live calls)
    """
    # Check mock calls first
    for call in CALL_LOG:
        if call.id == call_id:
            return call

    # Check live calls database
    live_call = db.query(LiveCall).filter(LiveCall.call_id == call_id).first()

    if live_call:
        # Convert to Call format
        return Call(
            id=live_call.call_id,
            time=live_call.start_time.strftime("%H:%M:%S") if live_call.start_time else "N/A",
            audio_file="",
            transcript=live_call.transcript or "",
            confidence=live_call.confidence_score or 0.0,
            pitch_avg=int(live_call.pitch_mean_hz) if live_call.pitch_mean_hz else 150,
            energy_avg=live_call.energy_rms or 0.0,
            distress_score=int(live_call.distress_score or 0),
            is_distress=(live_call.distress_score or 0) > 50,
            status=live_call.triage_queue or "LIVE-PROCESSED",
            location=live_call.location or "Jamaica (Location not specified)",
            category=live_call.category or "EMERGENCY CALL",
            lat=live_call.lat or 18.1096,
            lng=live_call.lng or -77.2975,
            nlp_extraction=None
        )

    raise HTTPException(status_code=404, detail=f"Call {call_id} not found")


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database statistics."""
    live_calls_count = db.query(LiveCall).count()
    return {
        "status": "healthy",
        "total_calls": len(CALL_LOG),
        "live_calls_saved": live_calls_count
    }


@app.get("/api/live-calls")
def get_live_calls(
    limit: int = 50,
    offset: int = 0,
    queue: str = None,
    db: Session = Depends(get_db)
):
    """
    Get saved live call records from database.

    Args:
        limit: Maximum number of records to return (default: 50)
        offset: Number of records to skip (default: 0)
        queue: Filter by triage queue (optional: "auto_logged", "human_review", "priority_dispatch")
        db: Database session (injected)

    Returns:
        List of live call records with full analysis
    """
    query = db.query(LiveCall).order_by(LiveCall.start_time.desc())

    # Filter by queue if specified
    if queue:
        query = query.filter(LiveCall.triage_queue == queue)

    # Apply pagination
    calls = query.offset(offset).limit(limit).all()

    return {
        "total": db.query(LiveCall).count(),
        "count": len(calls),
        "calls": [
            {
                "id": call.id,
                "call_id": call.call_id,
                "start_time": call.start_time.isoformat() if call.start_time else None,
                "end_time": call.end_time.isoformat() if call.end_time else None,
                "duration_seconds": call.duration_seconds,
                "transcript": call.transcript,
                "confidence_score": call.confidence_score,
                "distress_score": call.distress_score,
                "triage_queue": call.triage_queue,
                "priority_level": call.priority_level,
                "flag_audio_review": call.flag_audio_review,
                "escalation_required": call.escalation_required,
                "dispatcher_action": call.dispatcher_action,
                "triage_reasoning": call.triage_reasoning,
                "chunks_processed": call.chunks_processed,
                "status": call.status,
            }
            for call in calls
        ]
    }


@app.get("/api/live-calls/{call_id}")
def get_live_call_by_id(call_id: str, db: Session = Depends(get_db)):
    """
    Get a specific live call record by call_id.

    Args:
        call_id: Live call ID (e.g., "LIVE-A1B2C3D4")
        db: Database session (injected)

    Returns:
        Complete call record with full triage data
    """
    call = db.query(LiveCall).filter(LiveCall.call_id == call_id).first()

    if not call:
        raise HTTPException(status_code=404, detail=f"Live call {call_id} not found")

    return {
        "id": call.id,
        "call_id": call.call_id,
        "start_time": call.start_time.isoformat() if call.start_time else None,
        "end_time": call.end_time.isoformat() if call.end_time else None,
        "duration_seconds": call.duration_seconds,
        "transcript": call.transcript,
        "confidence_score": call.confidence_score,
        "distress_score": call.distress_score,
        "bio_acoustic": {
            "pitch_mean_hz": call.pitch_mean_hz,
            "pitch_cv": call.pitch_cv,
            "energy_rms": call.energy_rms,
            "jitter": call.jitter,
        },
        "triage": call.triage_data,  # Full JSON triage result
        "triage_queue": call.triage_queue,
        "priority_level": call.priority_level,
        "flag_audio_review": call.flag_audio_review,
        "escalation_required": call.escalation_required,
        "dispatcher_action": call.dispatcher_action,
        "triage_reasoning": call.triage_reasoning,
        "chunks_processed": call.chunks_processed,
        "total_audio_duration": call.total_audio_duration,
        "status": call.status,
        "created_at": call.created_at.isoformat() if call.created_at else None,
    }


@app.websocket("/ws/live")
async def websocket_live_call(websocket: WebSocket):
    """
    WebSocket endpoint for live audio processing.

    Client sends:
    - Binary audio chunks (Float32 PCM from Web Audio API)

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
            // Send PCM audio chunks as ArrayBuffer
            const audioBuffer = new Float32Array(...);
            ws.send(audioBuffer.buffer);
        };
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            // Handle updates based on data.type
        };
    """
    # Generate unique call ID
    call_id = f"LIVE-{uuid.uuid4().hex[:8].upper()}"

    # Handle the live call with preloaded shared services
    await handle_live_call(
        websocket,
        call_id,
        asr_service=asr_service,
        bio_processor=bio_processor,
        nlp_service=nlp_service,
        triage_engine=triage_engine
    )


@app.post("/api/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze uploaded audio file through TRIDENT processing pipeline.

    Processes audio through all three layers:
    1. Layer 1 (ASR): Caribbean-tuned speech recognition with confidence scoring
    2. Layer 2 (NLP): Entity extraction and content indicator scoring
    3. Layer 3 (Bio-Acoustic): Vocal distress detection via pitch/energy analysis
    4. Triage: Priority queue routing via 3D decision matrix (Confidence × Content × Concern)

    Args:
        file: Audio file (WAV, MP3, etc. - librosa handles most formats)

    Returns:
        Complete TRIDENT analysis:
        {
            "transcript": str,
            "confidence": float,
            "nlp": {
                "entities": {
                    "location": {...},
                    "mechanism_hazard": str,
                    "clinical_indicators": {...},
                    "scale": {...}
                },
                "content_score": float
            },
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

        # Layer 2: NLP entity extraction and content scoring
        logger.info("Running NLP entity extraction (Layer 2)...")
        nlp_result = nlp_service.extract_entities(
            transcript=asr_result["transcript"],
            confidence=asr_result["confidence"]
        )

        # Layer 3: Bio-acoustic distress detection
        logger.info("Running bio-acoustic analysis (Layer 3)...")
        bio_result = bio_processor.extract_features(temp_file_path)

        # Triage decision with 3D matrix
        logger.info("Generating triage decision (3D matrix)...")
        triage_result = triage_engine.generate_dispatcher_guidance(
            confidence=asr_result["confidence"],
            distress_score=bio_result["distress_score"],
            transcript=asr_result["transcript"],
            content_score=nlp_result["content_score"]
        )

        logger.info(f"Analysis complete: Queue={triage_result['queue']}, "
                   f"Confidence={asr_result['confidence']:.3f}, "
                   f"Content={nlp_result['content_score']:.3f}, "
                   f"Distress={bio_result['distress_score']:.3f}")

        # Cleanup temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        # Return complete analysis
        return {
            "transcript": asr_result["transcript"],
            "confidence": asr_result["confidence"],
            "nlp": {
                "entities": nlp_result["entities"],
                "content_score": nlp_result["content_score"]
            },
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
