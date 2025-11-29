import streamlit as st
import time

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Project Filter | SMG-Labs",
    layout="wide",
    page_icon="🚨"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Header branding */
    .brand-header {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-title {
        color: #00d4ff;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    .brand-subtitle {
        color: #888;
        font-size: 0.9rem;
        margin: 0;
    }
    .brand-logo {
        color: #ff6b6b;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    /* Status indicators */
    .status-active {
        background: #0f3d0f;
        color: #4ade80;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    /* Progress bar override for distress meter */
    .stProgress > div > div > div > div { 
        background: linear-gradient(90deg, #fbbf24 0%, #f87171 50%, #dc2626 100%);
    }
    
    /* Triage boxes */
    .highlight-red { 
        border: 2px solid #dc2626; 
        padding: 1.2rem; 
        border-radius: 8px; 
        background: linear-gradient(135deg, #1f1215 0%, #2d1619 100%);
        box-shadow: 0 0 20px rgba(220, 38, 38, 0.3);
    }
    .highlight-green { 
        border: 2px solid #22c55e; 
        padding: 1.2rem; 
        border-radius: 8px; 
        background: linear-gradient(135deg, #0f1f13 0%, #132d17 100%);
        box-shadow: 0 0 15px rgba(34, 197, 94, 0.2);
    }
    .highlight-red h3, .highlight-green h3 {
        margin-top: 0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #0f0f1a;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
    }
    
    /* Audio player */
    audio {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- MOCK DATABASE (PRE-COMPUTED RESULTS) ---
# 4 calls: 3 green (auto-logged), 1 red (human review)
# Locations reference actual areas affected by Hurricane Melissa (Oct 28, 2025)
# NLP extraction demonstrates the value of accurate Caribbean ASR
CALL_LOG = [
    {
        "id": "CALL-1042",
        "time": "14:02:15",
        "audio_file": "assets/call_1_calm.wav", 
        "transcript": "Reporting a downed utility pole on the main road into Black River. It is blocking the entrance to the hospital.",
        "confidence": 0.92,
        "pitch_avg": 135,
        "energy_avg": 0.02,
        "distress_score": 15,
        "is_distress": False,
        "status": "AUTO-LOGGED",
        "location": "Black River, St. Elizabeth",
        "category": "Infrastructure: Power",
        "nlp_extraction": {
            "location": "Main road, Black River",
            "landmark": "Hospital entrance",
            "hazard_type": "Downed utility pole",
            "blocked_access": "Yes - hospital",
            "people_count": None,
            "resource_need": "JPS / Line clearance crew"
        }
    },
    {
        "id": "CALL-1043",
        "time": "14:02:38",
        "audio_file": "assets/call_2_calm.wav",
        "transcript": "The bridge at Santa Cruz has high water levels. Traffic is not moving. The road is impassable.",
        "confidence": 0.88,
        "pitch_avg": 142,
        "energy_avg": 0.03,
        "distress_score": 22,
        "is_distress": False,
        "status": "AUTO-LOGGED",
        "location": "Santa Cruz, St. Elizabeth",
        "category": "Infrastructure: Roads",
        "nlp_extraction": {
            "location": "Santa Cruz Bridge",
            "landmark": None,
            "hazard_type": "Flooding - road impassable",
            "blocked_access": "Yes - bridge",
            "people_count": None,
            "resource_need": "Traffic diversion / NWA alert"
        }
    },
    {
        "id": "CALL-1044",
        "time": "14:03:01",
        "audio_file": "assets/call_3_calm.wav",
        "transcript": "Water service is currently off in the Savanna-la-Mar area. We have been without water since the storm passed.",
        "confidence": 0.91,
        "pitch_avg": 128,
        "energy_avg": 0.025,
        "distress_score": 18,
        "is_distress": False,
        "status": "AUTO-LOGGED",
        "location": "Savanna-la-Mar, Westmoreland",
        "category": "Infrastructure: Water",
        "nlp_extraction": {
            "location": "Savanna-la-Mar (area-wide)",
            "landmark": None,
            "hazard_type": "Water service outage",
            "blocked_access": None,
            "people_count": "Area-wide impact",
            "resource_need": "NWC restoration crew"
        }
    },
    {
        "id": "CALL-1045",  # THE HERO CALL - Patois under distress
        "time": "14:03:12",
        "audio_file": "assets/call_4_panic.wav",
        "transcript": "[wind/rain] ...di wata... [unintelligible] ...a mi waist... pickney dem... [crying] ...five a wi pan di roof... beg unnu send help now... [unintelligible]",
        "confidence": 0.31,
        "pitch_avg": 289,
        "energy_avg": 0.11,
        "distress_score": 94,
        "is_distress": True,
        "status": "HUMAN REVIEW",
        "location": "Unknown - Cell Tower: New Hope, St. Elizabeth",
        "category": "LIFE SAFETY",
        "nlp_extraction": {
            "location": "Rooftop (Cell tower: New Hope)",
            "landmark": None,
            "hazard_type": "Flood - Rising water",
            "blocked_access": "Trapped - cannot move",
            "people_count": "5 (includes children)",
            "resource_need": "IMMEDIATE EVACUATION - Boat/Helicopter"
        }
    }
]

# --- SESSION STATE ---
if 'selected_call' not in st.session_state:
    st.session_state.selected_call = CALL_LOG[0]

# --- HEADER BRANDING ---
st.markdown("""
<div class="brand-header">
    <div>
        <p class="brand-title">🚨 PROJECT FILTER</p>
        <p class="brand-subtitle">Crisis Triage Dashboard • ASR + NLP + Bio-Acoustic Intelligence</p>
    </div>
    <div style="text-align: right;">
        <p class="brand-logo">SMG-Labs</p>
        <p class="brand-subtitle">Caribbean Voices AI</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- REGION & STATUS BAR ---
col_region, col_status, col_calls = st.columns([2, 1, 1])
with col_region:
    st.markdown("**Active Region:** St. Elizabeth Parish, Jamaica")
with col_status:
    st.markdown('<span class="status-active">● HURRICANE MELISSA RESPONSE</span>', unsafe_allow_html=True)
with col_calls:
    pending = sum(1 for c in CALL_LOG if c['is_distress'])
    st.markdown(f"**Pending Human Review:** {pending}")

st.markdown("---")

# --- SIDEBAR (CALL FEED) ---
with st.sidebar:
    st.markdown("## 📡 Incoming Call Feed")
    st.caption("Click to inspect call details")
    st.markdown("---")
    
    for call in CALL_LOG:
        icon = "🔴" if call['is_distress'] else "🟢"
        status_text = "HUMAN" if call['is_distress'] else "AUTO"
        label = f"{icon} {call['time']} | {status_text}"
        
        # Highlight selected call
        button_type = "primary" if st.session_state.selected_call['id'] == call['id'] else "secondary"
        
        if st.button(label, key=call['id'], use_container_width=True, type=button_type):
            with st.spinner('Analyzing audio stream...'):
                time.sleep(0.7)
            st.session_state.selected_call = call
            st.rerun()
    
    st.markdown("---")
    st.caption("🟢 Auto-logged to Infrastructure DB")
    st.caption("🔴 Routed to Human Dispatcher")

# --- MAIN DASHBOARD ---
c = st.session_state.selected_call

# Top Metrics Row
st.markdown("### 📊 Call Analysis")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Call ID", c['id'])
col2.metric("Timestamp", c['time'])
col3.metric("ASR Confidence", f"{int(c['confidence']*100)}%")
col4.metric("Distress Score", f"{c['distress_score']}/100", 
            delta="CRITICAL" if c['distress_score'] > 60 else "Normal",
            delta_color="inverse" if c['distress_score'] > 60 else "off")
col5.metric("Category", c['category'])

st.markdown("---")

# Main Content Area
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown("### 🎧 Audio Source")
    try:
        st.audio(c['audio_file'])
    except:
        st.info("🎵 Audio placeholder - recording not yet loaded")
        st.caption(f"Expected file: `{c['audio_file']}`")
    
    st.markdown("### 📝 ASR Transcription")
    st.caption("Model: Whisper-Caribbean (Fine-tuned)")
    
    if c['is_distress']:
        st.error(c['transcript'])
        st.warning("⚠️ **Low Confidence Warning:** Transcript likely incomplete. Deep dialect and/or acoustic interference detected.")
    else:
        st.success(c['transcript'])
        st.caption("✅ High confidence transcription. Auto-logged to incident database.")
    
    st.markdown(f"**Detected Location:** {c['location']}")

with right_col:
    st.markdown("### 📈 Bio-Acoustic Analysis")
    st.caption("Domain-calibrated for Caribbean vocal patterns")
    
    # Distress Meter
    st.markdown("**Vocal Distress Severity**")
    st.progress(c['distress_score'] / 100)
    
    # Acoustic Metrics
    m1, m2 = st.columns(2)
    
    pitch_delta = "High" if c['pitch_avg'] > 240 else "Normal"
    energy_delta = "High" if c['energy_avg'] > 0.05 else "Normal"
    
    m1.metric(
        "Avg Pitch", 
        f"{c['pitch_avg']} Hz",
        delta=pitch_delta,
        delta_color="inverse" if c['pitch_avg'] > 240 else "off",
        help="Baseline: 100-180Hz. Values >240Hz indicate vocal stress/panic."
    )
    m2.metric(
        "Energy (RMS)", 
        f"{c['energy_avg']:.3f}",
        delta=energy_delta,
        delta_color="inverse" if c['energy_avg'] > 0.05 else "off",
        help="Baseline: 0.02-0.04. High values indicate shouting or loud environment."
    )
    
    st.markdown("---")
    
    # Routing Decision Box
    st.markdown("### 🤖 System Decision")
    
    if c['is_distress']:
        st.markdown("""
        <div class="highlight-red">
            <h3>🚨 PRIORITY ROUTING</h3>
            <p><strong>Trigger:</strong> Bio-Acoustic Distress (Score: {}) + Low ASR Confidence ({}%)</p>
            <p><strong>Action:</strong> Immediate routing to Human Dispatcher</p>
            <p><strong>Queue Position:</strong> #1 (Priority Override)</p>
        </div>
        """.format(c['distress_score'], int(c['confidence']*100)), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="highlight-green">
            <h3>✅ AUTO-LOGGED</h3>
            <p><strong>Trigger:</strong> Standard dialect + Calm vocal signature</p>
            <p><strong>Action:</strong> Logged to Infrastructure Incident Database</p>
            <p><strong>Category:</strong> {}</p>
        </div>
        """.format(c['category']), unsafe_allow_html=True)

# --- NLP EXTRACTION PANEL (Full Width) ---
st.markdown("---")
st.markdown("### 🧠 Local NLP Extraction")
st.caption("Entity extraction via Llama-3-8B (Offline via Ollama) • Enabled by accurate Caribbean ASR")

nlp = c.get('nlp_extraction', {})

# Display extracted entities in a structured grid
col_nlp1, col_nlp2, col_nlp3 = st.columns(3)

with col_nlp1:
    st.markdown("**📍 Location Intel**")
    st.info(f"**Location:** {nlp.get('location', 'N/A')}")
    if nlp.get('landmark'):
        st.info(f"**Landmark:** {nlp.get('landmark')}")
    if nlp.get('blocked_access'):
        st.warning(f"**Access:** {nlp.get('blocked_access')}")

with col_nlp2:
    st.markdown("**⚠️ Hazard Assessment**")
    hazard = nlp.get('hazard_type', 'N/A')
    if c['is_distress']:
        st.error(f"**Type:** {hazard}")
    else:
        st.warning(f"**Type:** {hazard}")
    
    if nlp.get('people_count'):
        pax = nlp.get('people_count')
        if c['is_distress']:
            st.error(f"**People:** {pax}")
        else:
            st.info(f"**People:** {pax}")

with col_nlp3:
    st.markdown("**🆘 Resource Dispatch**")
    need = nlp.get('resource_need', 'N/A')
    if c['is_distress']:
        st.error(f"**Need:** {need}")
    else:
        st.success(f"**Assign:** {need}")

# --- FOOTER ---
st.markdown("---")
st.caption("Project Filter • SMG-Labs • Caribbean Voices AI Hackathon 2025 • Hurricane Melissa Response Demo")
