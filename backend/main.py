from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import os

from models import Call
from data import CALL_LOG

app = FastAPI(title="TRIDENT API", version="1.0.0")

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
