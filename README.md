# Project Filter - Crisis Triage Dashboard

## SMG-Labs | Caribbean Voices AI Hackathon

**Context:** Hurricane Melissa Response Demo (October 28, 2025)
**Architecture:** FastAPI + React
**Innovation:** 3-Layer Crisis Triage System (Caribbean ASR → Local NLP → Bio-Acoustic Analysis)

---

## Quick Start

### Option 1: Using Start Scripts (Recommended)

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start-frontend.sh
```

Then open http://localhost:5173 in your browser.

### Option 2: Manual Start

**Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

---

## First Time Setup

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

---

## Project Structure

```
project_filter/
├── backend/                   # FastAPI REST API
│   ├── main.py               # API routes & CORS config
│   ├── models.py             # Pydantic data models
│   ├── data.py               # Mock call data (CALL_LOG)
│   ├── requirements.txt      # Python dependencies
│   └── venv/                 # Python virtual environment
├── frontend/                  # React + Vite SPA
│   ├── src/
│   │   ├── App.jsx           # Main dashboard component
│   │   ├── App.css           # Styling (ported from Streamlit)
│   │   └── components/
│   │       ├── CallFeed.jsx        # Sidebar call list
│   │       ├── CallMetrics.jsx     # Top metrics row
│   │       ├── AudioSection.jsx    # Audio player + transcript
│   │       ├── BioAcoustics.jsx    # Bio-acoustic analysis panel
│   │       └── NLPExtraction.jsx   # NLP entity extraction (NEW)
│   ├── package.json
│   └── vite.config.js        # Proxy config for API calls
├── assets/                    # Audio files (served by FastAPI)
│   ├── call_1_calm.wav       # Infrastructure report (calm)
│   ├── call_2_calm.wav       # Infrastructure report (calm)
│   ├── call_3_calm.wav       # Infrastructure report (calm)
│   └── call_4_panic.wav      # THE HERO CALL (Patois, distress)
├── start-backend.sh           # Backend start script
├── start-frontend.sh          # Frontend start script
└── app.py                     # Legacy Streamlit app (archived)
```

---

## The 3-Layer System

### Layer 1: Caribbean ASR (Whisper Fine-Tuned)
- Accurately transcribes Caribbean English and Patois
- Foundation for all downstream analysis
- **Without this, NLP extraction fails (garbage in, garbage out)**

### Layer 2: Local NLP Extraction (Llama-3-8B via Ollama)
- Runs offline - no internet required
- Extracts structured entities from transcripts:
  - `location` - Precise location with landmarks
  - `hazard_type` - Specific hazard classification
  - `blocked_access` - Access restrictions
  - `people_count` - Number of people affected
  - `resource_need` - Dispatch recommendations
- **Turns transcripts into dispatch orders**

### Layer 3: Bio-Acoustic Analysis
- Detects vocal distress even when ASR fails
- Measures pitch (vocal stress), energy (shouting), distress score
- **Safety net for deep Patois under extreme stress**
- Routes high-distress calls to human dispatchers

### The Pipeline in Action

**Green Calls (Standard dialect, calm):**
- ASR: 88-92% confidence → NLP extracts full dispatch order → Auto-logged

**Red Call (Patois, distress, background noise):**
- ASR: 31% confidence (partial transcription)
- Bio-Acoustic: Pitch 289 Hz, Energy 0.11, Distress 94
- NLP: Still extracts "5 people", "rooftop", "children", "immediate evacuation"
- **Result:** Priority routing with actionable rescue data

---

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs:** http://localhost:8000/docs
- **API Root:** http://localhost:8000/

### Endpoints

- `GET /api/calls` - Returns all calls with NLP extraction data
- `GET /api/calls/{call_id}` - Returns specific call
- `GET /health` - Health check

---

## Customizing the Dashboard

### To update the mock data:

Edit `backend/data.py` and modify the `CALL_LOG` list:

**ASR Fields:**
- `transcript`: What shows as the ASR output
- `confidence`: 0.0-1.0 (lower = worse transcription)

**Bio-Acoustic Fields:**
- `pitch_avg`: Hz value (>240 = distress indicator)
- `energy_avg`: RMS value (>0.05 = loud/distress)
- `distress_score`: 0-100 (>60 triggers red routing)

**NLP Extraction Fields:**
- `location`: Precise location intel
- `landmark`: Notable landmarks
- `hazard_type`: Hazard classification
- `blocked_access`: Access restrictions
- `people_count`: People affected (can be "5", "Area-wide", etc.)
- `resource_need`: Dispatch recommendations

### To add your audio files:

Simply replace the placeholder `.wav` files in `assets/` with your recordings.
Keep the same filenames, or update the `audio_file` paths in `backend/data.py`.

---

## Recording Guide

### The 3 Calm Calls (Green - Auto-Logged)

**Voice style:** Professional, measured, like calling a radio station to report road conditions.

**Call 1 - Power/Infrastructure:**
> "Good afternoon. I'm calling to report a downed utility pole on Nelson Street. It's blocking the main entrance to the hospital. No injuries that I can see."

**Call 2 - Roads/Flooding:**
> "Yes, I want to report that the bridge at Spanish Town Road has high water levels. Traffic is still moving but slowly. Drivers should use caution."

**Call 3 - Water Service:**
> "Hello, I'm calling from Portmore. Water service has been off since this morning. The whole area is affected. Just wanted to let you know."

**Tips for calm recordings:**
- Speak at normal pace
- Keep voice steady, no urgency
- Record in a quiet room
- Use your natural Caribbean accent (mesolect is fine)

---

### The Hero Call (Red - Human Review)

This is the emotional center of your demo. It needs to sound real.

**Setup:**
1. Download rain/wind ambient sound from YouTube Audio Library
2. Play it on your phone at ~30% volume while recording
3. Do 10 jumping jacks before recording to get slightly breathless
4. Record in a bathroom or closet (enclosed acoustic = "trapped" feeling)

**Script (Jamaican Patois version):**
> "Hello?! Hello?! Di wata a come eena di house! [pause, breathing]
> It deh a mi waist now! Mi pickney dem upstairs but wi cyaan move!
> [voice breaking] Lawd God, beg unnu send help!
> Wi deh pon [your location/make one up] ...please... [crying/distress sounds]"

**Translation for reference:**
> "Hello?! Hello?! The water is coming into the house!
> It's at my waist now! My children are upstairs but we can't move!
> Lord God, please send help!
> We are at [location] ...please..."

**Alternative - Trinidadian Creole:**
> "Aye! Aye! De water coming in de house!
> It reach mih waist! Mih children upstairs, we cyah move!
> Please, ah beg yuh, send help now now!
> We in [location]... [crying]"

**Tips for distress recording:**
- Don't act - actually get yourself slightly worked up
- Speak faster than normal
- Let your voice pitch rise naturally
- It's okay to stumble over words
- Real panic is messy - embrace that

---

## Demo Flow for Pitch Video

See [PITCH_SCRIPT.md](PITCH_SCRIPT.md) for the complete 3-minute video script.

**Quick Demo Notes:**

1. **Call 1 (Green):** ASR 92% → NLP extracts "Hospital entrance blocked, JPS crew needed" → Auto-logged
2. **Call 2 (Green):** ASR 88% → NLP extracts "Santa Cruz bridge flooded, traffic diversion needed" → Auto-logged
3. **Call 3 (Green):** ASR 91% → NLP extracts "Savanna-la-Mar water outage, NWC crew needed" → Auto-logged
4. **Call 4 (RED):** ASR 31% → Bio-Acoustic detects distress (289 Hz pitch) → NLP still extracts "5 people, rooftop, children, evacuation needed" → Priority routing

**Key Message:** Caribbean ASR is the foundation. Without accurate transcription, NLP cannot extract actionable intelligence. The bio-acoustic layer ensures high-distress calls never get lost, even when ASR fails.

---

## Architecture Notes

### Why FastAPI + React?

- **Separation of Concerns:** API can be consumed by multiple clients
- **Scalability:** Easier to deploy backend/frontend independently
- **Modern Stack:** Industry-standard tooling for production apps
- **Developer Experience:** Fast HMR with Vite, auto-docs with FastAPI

### Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- Uvicorn - ASGI server
- Pydantic - Data validation with NLP extraction models

**Frontend:**
- React 19 - UI library
- Vite - Build tool & dev server
- Axios - HTTP client

**Production AI Stack (Not Implemented in Demo):**
- Whisper (fine-tuned on Caribbean broadcast data) - ASR
- Llama-3-8B via Ollama - Local NLP extraction
- Librosa - Bio-acoustic feature extraction

**Demo Note:** This dashboard uses pre-computed mock data to simulate the 3-layer system. In production, audio would be processed through the actual AI pipeline.

---

## Troubleshooting

**Backend won't start?**
- Check Python version (3.8+): `python3 --version`
- Make sure virtual environment is activated
- Try: `pip install --upgrade fastapi uvicorn`

**Frontend won't start?**
- Check Node.js version (18+): `node --version`
- Try: `npm install` in the frontend directory
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

**Audio not playing?**
- Make sure files are `.wav` format
- Check file paths match exactly in `backend/data.py`
- Verify backend is serving static files: http://localhost:8000/assets/call_1_calm.wav
- Try converting with: `ffmpeg -i input.m4a -ar 22050 output.wav`

**CORS errors?**
- Make sure backend is running on port 8000
- Frontend should proxy requests via Vite config
- Check `frontend/vite.config.js` proxy settings

**Port already in use?**
- Backend (8000): `lsof -ti:8000 | xargs kill -9`
- Frontend (5173): `lsof -ti:5173 | xargs kill -9`

---

## Project Context

**Hurricane Melissa - October 28, 2025**
- Category 5, 185 mph winds
- Strongest storm to hit Jamaica since 1851
- Black River, St. Elizabeth Parish was ground zero
- <50% of the island had communications post-storm
- 77% of Jamaica lost power
- $6 billion in damage (30% of Jamaica's GDP)

**The Problem:**
Emergency dispatchers were overwhelmed. Standard ASR systems failed on deep Patois spoken under stress. The most vulnerable calls became invisible to the system.

**The Solution:**
Caribbean-calibrated ASR + Local NLP + Bio-Acoustic triage. When words fail, vocal stress patterns route the call to human dispatchers.

---

Built for the Caribbean Voices AI Hackathon 2025
**SMG-Labs:** Elroy, Chad, Donahue

*"We turn voices into rescue missions."*
