# Project Filter - Crisis Triage Dashboard

## SMG-Labs | Caribbean Voices AI Hackathon

**Architecture:** FastAPI + React (refactored from Streamlit for scalability)

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
│   │       ├── CallFeed.jsx       # Sidebar call list
│   │       ├── CallMetrics.jsx    # Top metrics row
│   │       ├── AudioSection.jsx   # Audio player + transcript
│   │       └── BioAcoustics.jsx   # Bio-acoustic analysis panel
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

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs:** http://localhost:8000/docs
- **API Root:** http://localhost:8000/

### Endpoints

- `GET /api/calls` - Returns all calls
- `GET /api/calls/{call_id}` - Returns specific call
- `GET /health` - Health check

---

## Customizing the Dashboard

### To update the mock data:

Edit `backend/data.py` and modify the `CALL_LOG` list:
- `transcript`: What shows as the ASR output
- `confidence`: 0.0-1.0 (lower = worse transcription)
- `pitch_avg`: Hz value (>240 = distress indicator)
- `energy_avg`: RMS value (>0.05 = loud/distress)
- `distress_score`: 0-100 (>60 triggers red routing)

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

## Demo Script for Video

**[Start with dashboard showing Call 1 selected]**

"Here's a standard infrastructure call. The system detects steady pitch at 135 hertz,
high ASR confidence. It automatically transcribes and logs the downed pole location.
No human dispatcher needed."

**[Click Call 2, wait for spinner]**

"Another routine report - high water on Spanish Town Road. Again, auto-logged.
The system is clearing the queue."

**[Click Call 4 (the red one), wait for spinner]**

"But then... this call comes in. Listen to the transcript - it's fragmented, incomplete.
The ASR confidence drops to 31 percent. But look at the right side:
pitch spikes to 289 hertz. Energy at 0.11. The Bio-Acoustic layer recognizes
the sound of panic - even when it can't understand the words.

Distress score: 94. The system doesn't try to auto-log this.
It immediately routes to the human dispatcher, queue position one.

This is the filter in action. We handle the volume, so humans can hear the signal."

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
- Pydantic - Data validation

**Frontend:**
- React 19 - UI library
- Vite - Build tool & dev server
- Axios - HTTP client

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

**Refactored to FastAPI + React architecture for pitch competition demo**
