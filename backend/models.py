from pydantic import BaseModel
from typing import Optional


class NLPExtraction(BaseModel):
    location: Optional[str] = None
    landmark: Optional[str] = None
    hazard_type: Optional[str] = None
    blocked_access: Optional[str] = None
    people_count: Optional[str] = None
    resource_need: Optional[str] = None


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
    lat: float
    lng: float
    nlp_extraction: Optional[NLPExtraction] = None
