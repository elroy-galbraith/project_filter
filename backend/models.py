from pydantic import BaseModel
from typing import Optional


class Call(BaseModel):
    id: str
    time: str
    audio_file: str
    transcript: str
    confidence: float
    pitch_avg: int
    energy_avg: float
    distress_score: int
    is_distress: bool
    status: str
    location: str
    category: str
