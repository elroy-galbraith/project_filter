# Project Filter - Crisis Triage Dashboard

## SMG-Labs | Caribbean Voices AI Hackathon

### The Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     INCOMING VOICE CALL                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: CARIBBEAN ASR (Whisper Fine-tuned)                    │
│  ─────────────────────────────────────────────                  │
│  • Accurate transcription of Caribbean accents                  │
│  • Handles mesolect/standard Caribbean English                  │
│  • Outputs: transcript + confidence score                       │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  LAYER 2: LOCAL NLP          │  │  LAYER 3: BIO-ACOUSTIC       │
│  (Llama 3 via Ollama)        │  │  (Librosa)                   │
│  ────────────────────────    │  │  ────────────────────────    │
│  • Entity extraction         │  │  • Pitch analysis (f0)       │
│  • Location, hazard, people  │  │  • Energy/volume (RMS)       │
│  • Resource needs            │  │  • Distress scoring          │
│  • Works even on partial     │  │  • Works even when ASR fails │
│    transcripts               │  │                              │
└──────────────────────────────┘  └──────────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TRIAGE DECISION                             │
│  ─────────────────────────────────────────────                  │
│  HIGH confidence + LOW distress  → AUTO-LOG (dispatch order)   │
│  LOW confidence + HIGH distress  → HUMAN REVIEW (priority #1)  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight: Garbage In, Garbage Out**

Without accurate Caribbean ASR, the NLP layer fails. Standard Whisper transcribes 
"Di bush fire deh near di gully bank" as "The bush fire day near the gulley bank" 
— and the LLM can't extract actionable intelligence from garbled input.

Our ASR is the key that turns the engine on.

**Offline Resilience**

The entire stack runs locally:
- Whisper (fine-tuned) - local GPU
- Llama 3 via Ollama - local GPU  
- Librosa - CPU

No internet required. Works when cell towers are the only thing standing.

---

### Beyond Hurricanes: Universal Emergency Triage

While Hurricane Melissa is our narrative anchor, Project Filter's architecture is **emergency-agnostic**. The core problem—Caribbean voices being misunderstood by standard technology, leading to delayed or failed emergency response—exists across all emergency services.

| Emergency Service | Use Cases | NLP Extracts |
|-------------------|-----------|--------------|
| **ODPEM / Disaster Response** | Hurricanes, floods, earthquakes, landslides | Location, hazard type, trapped persons, resource needs |
| **Police / 119** | Crime reports, domestic disturbances, traffic accidents | Location, suspect description, weapon present, victim count |
| **Fire Services** | Structure fires, bush fires, rescue operations | Location, fire type, trapped persons, hazmat indicators |
| **Ambulance / Medical** | Health emergencies, overdoses, accidents | Symptoms, patient condition, injured count, consciousness |
| **Utilities (JPS, NWC)** | Gas leaks, electrical hazards, water main breaks | Location, hazard type, affected area, immediate danger |
| **Coast Guard** | Maritime distress, drowning, boat emergencies | Vessel location, persons aboard, nature of distress |

**Why this matters:**

1. **Code-switching under stress happens in ALL emergencies** - A robbery victim reverts to Patois just like a flood victim does
2. **Dispatcher overload is universal** - Every call center struggles with volume triage
3. **Caribbean accents are underserved everywhere** - Not just during hurricane season

**Go-to-market advantage:**

- Easier to pilot: Any parish police station can test it, not just ODPEM during hurricane season
- Year-round value: Not seasonal infrastructure
- Multiple entry points: Police, fire, medical, utilities all need this

---

### Quick Start

**Architecture:** FastAPI (backend) + React (frontend)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

**Or use the convenience scripts:**
```bash
./start-backend.sh    # Terminal 1
./start-frontend.sh   # Terminal 2
```

---

## First Time Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
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
│   ├── models.py             # Pydantic models (Call, NLPExtraction)
│   ├── data.py               # Mock call data with NLP extractions
│   ├── requirements.txt      # Python dependencies
│   └── venv/                 # Python virtual environment
├── frontend/                  # React + Vite SPA
│   ├── src/
│   │   ├── App.jsx           # Main dashboard component
│   │   ├── App.css           # Styling
│   │   └── components/
│   │       ├── CallFeed.jsx        # Sidebar call list
│   │       ├── CallMetrics.jsx     # Top metrics row
│   │       ├── AudioSection.jsx    # Audio player + transcript
│   │       ├── BioAcoustics.jsx    # Bio-acoustic analysis panel
│   │       └── NLPExtraction.jsx   # NLP entity extraction panel
│   ├── package.json
│   └── vite.config.js        # Proxy config for API calls
├── assets/                    # Audio files (served by FastAPI)
│   ├── call_1_calm.wav       # Infrastructure report (calm, standard English)
│   ├── call_2_calm.wav       # Infrastructure report (calm, standard English)
│   ├── call_3_calm.wav       # Infrastructure report (calm, standard English)
│   └── call_4_panic.wav      # THE HERO CALL (Patois, distress, background noise)
├── start-backend.sh           # Backend start script
├── start-frontend.sh          # Frontend start script
├── app.py                     # Legacy Streamlit version (archived)
├── app_v2.py                  # Streamlit v2 with NLP (archived)
└── README.md
```

---

## Recording Guide

**Context:** These recordings simulate calls during the Hurricane Melissa response (October 28, 2025). The locations reference actual areas devastated by Melissa - Black River, Santa Cruz, and Savanna-la-Mar in St. Elizabeth and Westmoreland parishes.

### The 3 Calm Calls (Green - Auto-Logged)

**Voice style:** Professional, measured, like calling a radio station to report road conditions.

**Call 1 - Power/Infrastructure (Black River):**
> "Good afternoon. I'm calling to report a downed utility pole on the main road into Black River. It's blocking the entrance to the hospital. No injuries that I can see."

**Call 2 - Roads/Flooding (Santa Cruz):**
> "Yes, I want to report that the bridge at Santa Cruz has high water levels. Traffic is not moving. The road is impassable."

**Call 3 - Water Service (Savanna-la-Mar):**
> "Hello, I'm calling from Savanna-la-Mar. Water service has been off since the storm passed. The whole area is affected. Just wanted to let you know."

**Tips for calm recordings:**
- Speak at normal pace
- Keep voice steady, no urgency
- Record in a quiet room
- Use your natural Caribbean accent (mesolect is fine)

---

### The Hero Call (Red - Human Review)

This is the emotional center of your demo. It needs to sound real.

**Context:** This caller is trapped in New Hope, St. Elizabeth - near where Melissa made landfall with 185 mph winds. Their house is flooding. They have children upstairs.

**Setup:**
1. Download rain/wind ambient sound from YouTube Audio Library
2. Play it on your phone at ~30% volume while recording
3. Do 10 jumping jacks before recording to get slightly breathless
4. Record in a bathroom or closet (enclosed acoustic = "trapped" feeling)

**Script (Jamaican Patois version):**
> "Hello?! Hello?! Di wata a come eena di house! [pause, breathing] 
> It deh a mi waist now! Mi pickney dem upstairs but wi cyaan move! 
> [voice breaking] Lawd God, beg unnu send help! 
> Wi deh New Hope... near di church... [crying] ...please... please..."

**Translation for reference:**
> "Hello?! Hello?! The water is coming into the house!
> It's at my waist now! My children are upstairs but we can't move!
> Lord God, please send help!
> We're in New Hope... near the church... please..."

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
- The word "pickney" (children) is your emotional anchor - let your voice break there

---

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs:** http://localhost:8000/docs
- **API Root:** http://localhost:8000/

**Endpoints:**
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

## Demo Script for Video

See **PITCH_SCRIPT.md** for the full 3-minute video script with timing cues.

**Quick reference for click-through:**

**[Start with dashboard showing Call 1 selected]**

"This caller reports a downed utility pole blocking the road into Black River hospital. 
Confidence: 92 percent. 

But look at the NLP extraction panel below. Because our ASR got the words right, 
the local LLM extracts structured data: Location—main road, Black River. 
Blocked access—hospital. Resource needed—JPS line crew.

This call just became a dispatch order."

**[Click Call 2, wait for spinner]**

"Santa Cruz bridge flooding. NLP extracts: road impassable, needs traffic diversion."

**[Click Call 3, wait for spinner]**  

"Water outage in Savanna-la-Mar. Extracted: area-wide impact, assign NWC crew.
Three calls. Three structured dispatch orders."

**[Click Call 4 (the red one), wait for spinner]**

"This call just came in. New Hope, St. Elizabeth - near where Melissa made landfall.
Cell tower only, no address.

Look at the transcript - fragmented. 'Di wata... a mi waist... pickney dem... five a wi pan di roof...'
Confidence: 31 percent. Standard system stops here. Failed transcription.

But look at the bio-acoustic analysis on the right. Pitch: 289 hertz - vocal panic.
Energy at 0.11 - shouting through wind and rain. Distress score: 94.

And scroll down to the NLP extraction panel. Here's what's remarkable - even with partial
transcription, the LLM still extracts what it can:

Location: Rooftop (Cell tower: New Hope)
People: 5 (includes children)
Hazard: Flood - Rising water
Blocked access: Trapped - cannot move
Resource need: IMMEDIATE EVACUATION - Boat/Helicopter

The system doesn't just flag this for human review. It hands the dispatcher a structured
rescue mission with everything they need to launch a response.

That mother - and her four children - just jumped to the front of the line.

We built this for hurricane response. But the architecture works for any emergency
call center in the Caribbean - police, fire, ambulance. Anywhere Caribbean voices
need to be understood when it matters most."

---

## Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- Uvicorn - ASGI server
- Pydantic - Data validation with NLP extraction models

**Frontend:**
- React 19 - UI library
- Vite - Build tool & dev server
- Axios - HTTP client

**Production AI Stack (Simulated in Demo):**
- Whisper (fine-tuned on Caribbean broadcast data) - ASR
- Llama-3-8B via Ollama - Local NLP extraction
- Librosa - Bio-acoustic feature extraction

**Demo Note:** This dashboard uses pre-computed mock data to demonstrate the 3-layer system. In production, audio would be processed through the actual AI pipeline in real-time.

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

Built for the Caribbean Voices AI Hackathon 2025
SMG-Labs: Elroy, Chad, Donahue

*"We turn voices into rescue missions."*

**Target Applications:** ODPEM, 119/Police, Fire Services, Ambulance/Medical, Utilities, Coast Guard — any Caribbean emergency call center where being understood is the difference between life and death.
