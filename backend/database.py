"""
SQLAlchemy Database Configuration and Models for TRIDENT

Provides persistent storage for live call records including:
- Call metadata (ID, timestamps, duration)
- Transcription results
- Bio-acoustic analysis (confidence, distress scores)
- Triage decisions (queue assignment, priority level)
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trident_calls.db")

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class LiveCall(Base):
    """
    Database model for live call records.

    Stores complete analysis from real-time processing including
    ASR transcription, bio-acoustic features, and triage decisions.
    """
    __tablename__ = "live_calls"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    call_id = Column(String, unique=True, index=True, nullable=False)  # e.g., "LIVE-A1B2C3D4"

    # Timing
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Audio metadata
    chunks_processed = Column(Integer, default=0)
    total_audio_duration = Column(Float, nullable=True)

    # ASR Layer (Layer 1)
    transcript = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0 - 1.0

    # NLP Layer (Layer 2)
    content_score = Column(Float, nullable=True)  # 0.0 - 1.0

    # Bio-Acoustic Layer (Layer 3)
    distress_score = Column(Float, nullable=True)  # 0.0 - 100.0
    pitch_mean_hz = Column(Float, nullable=True)
    pitch_cv = Column(Float, nullable=True)
    energy_rms = Column(Float, nullable=True)
    jitter = Column(Float, nullable=True)

    # Triage Decision
    triage_queue = Column(String, nullable=True)  # "auto_logged", "human_review", "priority_dispatch"
    priority_level = Column(Integer, nullable=True)  # 1 (highest) - 5 (lowest)
    flag_audio_review = Column(Boolean, default=False)
    escalation_required = Column(Boolean, default=False)
    dispatcher_action = Column(Text, nullable=True)
    triage_reasoning = Column(Text, nullable=True)

    # Full triage result as JSON for extensibility
    triage_data = Column(JSON, nullable=True)

    # Location Data (for map visualization)
    location = Column(String, nullable=True)  # Human-readable location (e.g., "Kingston, Jamaica")
    lat = Column(Float, nullable=True)  # Latitude
    lng = Column(Float, nullable=True)  # Longitude
    category = Column(String, nullable=True)  # Call category (e.g., "LIFE SAFETY", "Infrastructure")

    # Call status
    status = Column(String, default="completed")  # "completed", "error", "interrupted"
    error_message = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<LiveCall {self.call_id} - Queue: {self.triage_queue}, Confidence: {self.confidence_score:.2f}>"


def init_db():
    """
    Initialize database and create tables.

    Call this at application startup to ensure database schema exists.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Get database session (for dependency injection in FastAPI).

    Usage:
        @app.get("/calls")
        def get_calls(db: Session = Depends(get_db)):
            return db.query(LiveCall).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
