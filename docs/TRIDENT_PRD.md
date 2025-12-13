# TRIDENT Product Requirements Document

**Version:** 1.0  
**Date:** December 13, 2025  
**Status:** Pre-Demo Build Assessment  
**Authors:** SMG Labs Research Group

---

## Executive Summary

This PRD maps the TRIDENT architecture (as documented in the white paper) against current implementation status to identify what remains to be built before the live pitch demo and for production deployment.

**Current State:** Core ASR model fine-tuned; remaining layers unbuilt  
**Demo Date:** December 13, 2025 (today)  
**Demo Goal:** Prove edge deployment viability on laptop hardware

---

## 1. System Components & Implementation Status

### Legend
- ✅ **DONE** — Implemented and tested
- 🟡 **PARTIAL** — Started but incomplete
- ❌ **NOT STARTED** — Needs to be built
- 🎯 **DEMO CRITICAL** — Required for live pitch

---

## 2. Layer 1: Caribbean-Tuned ASR

| Requirement | Spec (from paper) | Actual | Status |
|-------------|-------------------|--------|--------|
| Base model | Whisper Medium | Whisper Large | ✅ (better) |
| Fine-tuning method | LoRA (rank=16, α=32) | LoRA | ✅ |
| Training data | BBC Caribbean corpus (~28k clips) | BBC Caribbean corpus | ✅ |
| Model artifacts | Stored locally | Google Drive (checkpoint-1398) | ✅ |
| Confidence scoring | Mean log-prob, normalized 0-1 | **NOT IMPLEMENTED** | ❌ 🎯 |
| Confidence threshold | 0.7 | N/A | ❌ |

### What's Built
- Fine-tuned Whisper Large model on Caribbean broadcast speech
- Model weights saved and available in Google Drive

### What's Missing (Demo Critical)
```python
# Need to implement confidence extraction:
def get_confidence(model, inputs):
    """
    Compute utterance-level confidence as mean log-probability
    confidence = exp(mean(log_probs))
    Returns: float in [0, 1]
    """
    # Paper spec: Equation (1), Section 4.2
```

### Build Estimate
- Confidence scoring: **30 minutes**

---

## 3. Layer 2: NLP Entity Extraction

| Requirement | Spec (from paper) | Status |
|-------------|-------------------|--------|
| Model | Llama 3 8B (4-bit quantized) | ❌ |
| Serving | Ollama (local) | ❌ |
| Entity schema | LOCATION, MECHANISM, CLINICAL, SCALE | ❌ |
| Content Indicator Score (Sc) | Deterministic scoring function | ❌ |
| Confidence-aware prompting | Low-confidence transcript handling | ❌ |

### Entity Extraction Schema (from Section 4.3.1)
```json
{
  "location": "Street addresses, landmarks, geographic references",
  "mechanism_hazard": "fire | flood | medical | violence | traffic | infrastructure | other",
  "clinical_indicators": {
    "breathing": "normal | impaired | not_breathing",
    "consciousness": "alert | altered | unresponsive",
    "bleeding": "none | minor | heavy",
    "mobility": "walking | impaired | immobile"
  },
  "scale": {
    "persons_affected": "integer",
    "vulnerable_population": "boolean"
  }
}
```

### Content Indicator Score (from Section 4.3.4)
```python
# Sc = min(100, S_hazard + S_threat + S_vuln + S_scale)
#
# Hazard weights: violent_crime=30, fire=25, medical=20, flood=20, 
#                 traffic=15, infrastructure=10, other=5
# Life threat: imminent=+30, potential=+15, none=+0
# Vulnerable population: +15
# Scale: +5 per person (cap +20), escalating +10
```

### What's Missing
- Ollama installation with Llama 3 8B
- Prompt template for entity extraction
- Content scoring function
- Low-confidence handling logic

### Build Estimate
- Basic entity extraction: **2-3 hours**
- Content indicator scoring: **1 hour**
- **For demo:** Could skip entirely — show ASR + bio-acoustic only

---

## 4. Layer 3: Bio-Acoustic Distress Detection

| Requirement | Spec (from paper) | Status |
|-------------|-------------------|--------|
| F0 extraction | pYIN via librosa | ❌ 🎯 |
| F0 coefficient of variation | σ_F0 / μ_F0 | ❌ 🎯 |
| RMS energy | Normalized 0-1 | ❌ 🎯 |
| Jitter | Cycle-to-cycle F0 variation | ❌ 🎯 |
| Sex-adaptive thresholds | F0 < 165Hz → male params | ❌ |
| Distress score (D) | Weighted composite 0-1 | ❌ 🎯 |

### Distress Score Formula (from Section 4.4.2)
```python
D = 0.30 * P + 0.35 * V + 0.20 * E + 0.15 * J

# Where:
# P = pitch elevation (sex-adaptive)
# V = pitch instability (CV normalized)
# E = energy (RMS normalized)
# J = jitter (perturbation)

# Sex-adaptive pitch:
# Male (F0_init < 165Hz):   P = (F0 - 120) / 80
# Female (F0_init >= 165Hz): P = (F0 - 200) / 100
```

### Threshold Classification
- **High Distress:** D > 0.5
- **Low Distress:** D ≤ 0.5

### What's Missing
- Complete bio-acoustic feature extraction pipeline
- Distress score computation
- Sex-adaptive baseline detection

### Build Estimate
- Feature extraction: **1-2 hours**
- Distress scoring: **30 minutes**
- **This is demo-critical** — shows the "uncertainty as signal" insight

---

## 5. Queue Prioritization Engine

| Requirement | Spec (from paper) | Status |
|-------------|-------------------|--------|
| 3D decision matrix | Confidence × Content × Concern | ❌ |
| Q1-IMMEDIATE routing | Low Conf + High Distress | ❌ |
| Q2-ELEVATED routing | High Content indicators | ❌ |
| Early exit logic | D > 0.8 && C < 0.4 → immediate | ❌ |

### Priority Matrix (from Table 3)
| Confidence | Content | Concern | Queue |
|------------|---------|---------|-------|
| High | Low | Low | Q5-ROUTINE |
| High | High | Low | Q2-ELEVATED |
| High | Low | High | Q3-MONITOR |
| High | High | High | Q1-IMMEDIATE |
| Low | Low | Low | Q5-REVIEW |
| Low | High | Low | Q2-ELEVATED |
| Low | Low | High | Q1-IMMEDIATE |
| Low | High | High | Q1-IMMEDIATE |

### Build Estimate
- Matrix logic: **30 minutes**
- **For demo:** Nice to have, not critical

---

## 6. Dispatcher Interface

| Requirement | Spec (from paper) | Status |
|-------------|-------------------|--------|
| Queue priority display | Visual urgency coding | ❌ |
| Confidence flag | "Review audio" recommendation | ❌ |
| Entity display | Structured clinical indicators | ❌ |
| Bio-acoustic indicators | Distress score + components | ❌ |
| Audio playback | One-click access | ❌ |
| Map integration | Location visualization | ❌ |

### Build Estimate
- Minimal Streamlit demo: **2-3 hours**
- Full interface (as shown in Figure 3): **1-2 days**

---

## 7. Demo Build Plan (Priority Order)

### Tier 1: Must Have for Pitch (Today)
| Component | Time | Purpose |
|-----------|------|---------|
| ASR inference script (M1 MPS) | 30 min | Prove laptop deployment |
| Confidence scoring | 30 min | Show "uncertainty as signal" |
| Bio-acoustic extraction | 1.5 hr | Show parallel signal path |
| Distress score | 30 min | Complete the 3C framework |
| **Total Tier 1** | **~3 hours** | |

### Tier 2: Nice to Have
| Component | Time | Purpose |
|-----------|------|---------|
| Simple Streamlit UI | 2 hr | Visual impact |
| Queue priority logic | 30 min | Show prioritization |
| **Total Tier 2** | **~2.5 hours** | |

### Tier 3: Skip for Demo
| Component | Reason |
|-----------|--------|
| NLP entity extraction | Requires Ollama setup, time-consuming |
| Content indicator scoring | Depends on NLP layer |
| Full dispatcher interface | Post-demo deliverable |

---

## 8. Minimum Viable Demo Script

```python
"""
TRIDENT Demo - Minimum Viable Implementation
Shows: ASR + Confidence + Bio-Acoustic Distress
Proves: Edge deployment on M1 Mac
"""

from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch
import librosa
import numpy as np

MODEL_PATH = "./final_model"

# === LAYER 1: ASR with Confidence ===
def transcribe_with_confidence(audio_path):
    """Returns transcript + confidence score"""
    # Load audio
    audio, sr = librosa.load(audio_path, sr=16000)
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt")
    
    # Generate with scores
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_features.to(device),
            return_dict_in_generate=True,
            output_scores=True
        )
    
    # Compute confidence (mean log-prob)
    scores = torch.stack(outputs.scores, dim=1)
    log_probs = torch.log_softmax(scores, dim=-1)
    token_log_probs = log_probs.gather(2, outputs.sequences[:, 1:].unsqueeze(-1)).squeeze(-1)
    confidence = torch.exp(token_log_probs.mean()).item()
    
    transcript = processor.batch_decode(outputs.sequences, skip_special_tokens=True)[0]
    return transcript, confidence

# === LAYER 3: Bio-Acoustic Distress ===
def compute_distress(audio_path):
    """Returns distress score (0-1) and components"""
    y, sr = librosa.load(audio_path, sr=16000)
    
    # F0 extraction
    f0, voiced_flag, _ = librosa.pyin(y, fmin=50, fmax=400, sr=sr)
    f0_voiced = f0[voiced_flag]
    
    if len(f0_voiced) == 0:
        return 0.0, {}
    
    f0_mean = np.mean(f0_voiced)
    f0_std = np.std(f0_voiced)
    f0_cv = f0_std / f0_mean if f0_mean > 0 else 0
    
    # Sex-adaptive pitch elevation
    if f0_mean < 165:  # Estimated male
        P = min(1.0, max(0, (f0_mean - 120) / 80))
    else:  # Estimated female
        P = min(1.0, max(0, (f0_mean - 200) / 100))
    
    # Pitch instability
    V = min(1.0, f0_cv / 0.5)
    
    # Energy
    rms = librosa.feature.rms(y=y)[0]
    E = min(1.0, np.mean(rms) / 0.1)
    
    # Jitter (simplified)
    if len(f0_voiced) > 1:
        jitter = np.mean(np.abs(np.diff(f0_voiced))) / f0_mean
        J = min(1.0, jitter / 0.02)
    else:
        J = 0.0
    
    # Weighted composite
    D = 0.30 * P + 0.35 * V + 0.20 * E + 0.15 * J
    
    return D, {
        "f0_mean": f0_mean,
        "f0_cv": f0_cv,
        "pitch_elevation": P,
        "instability": V,
        "energy": E,
        "jitter": J
    }

# === DEMO OUTPUT ===
def analyze_call(audio_path):
    transcript, confidence = transcribe_with_confidence(audio_path)
    distress, components = compute_distress(audio_path)
    
    # Determine queue priority (simplified)
    if confidence < 0.7 and distress > 0.5:
        queue = "Q1-IMMEDIATE"
    elif confidence >= 0.7 and distress > 0.5:
        queue = "Q3-MONITOR"
    elif confidence < 0.7:
        queue = "Q5-REVIEW"
    else:
        queue = "Q5-ROUTINE"
    
    return {
        "transcript": transcript,
        "confidence": confidence,
        "distress_score": distress,
        "distress_components": components,
        "queue_priority": queue,
        "flag_audio_review": confidence < 0.7
    }
```

---

## 9. Test Scenarios for Demo

### Scenario A: Clear Acrolect (High Confidence)
- **Input:** Caribbean speaker, standard English, calm
- **Expected:** High confidence (>0.7), low distress (<0.5)
- **Queue:** Q5-ROUTINE
- **Shows:** System works on clear speech

### Scenario B: Stressed Basilect (Low Confidence + High Distress)
- **Input:** Caribbean speaker, creole-heavy, elevated stress
- **Expected:** Low confidence (<0.7), high distress (>0.5)
- **Queue:** Q1-IMMEDIATE
- **Shows:** Core insight — ASR failure becomes prioritization signal

### Scenario C: Calm Professional (High Confidence + Semantic Urgency)
- **Input:** Clear speech reporting serious emergency calmly
- **Expected:** High confidence, low distress
- **Queue:** Would be Q2-ELEVATED with NLP layer
- **Note:** Without NLP, this goes to Q5-ROUTINE (limitation to acknowledge)

---

## 10. Post-Demo Roadmap

| Phase | Components | Timeline |
|-------|------------|----------|
| Demo (Dec 13) | ASR + Confidence + Bio-acoustic | Today |
| MVP (Jan 2026) | + NLP entity extraction | 2 weeks |
| Alpha (Feb 2026) | + Dispatcher UI + queue logic | 4 weeks |
| Pilot (Q2 2026) | + Ministry partnership + real call testing | 3 months |

---

## 11. Hardware Requirements Summary

### Demo (M1 Pro MacBook)
| Component | Size | Speed |
|-----------|------|-------|
| Whisper Large | ~3GB | 1-2x realtime on MPS |
| Bio-acoustic | <50MB | Real-time |
| **Total** | ~3GB | Viable |

### Production (Raspberry Pi 5)
| Component | Size | Speed |
|-----------|------|-------|
| Whisper Medium (INT4) | ~400MB | ~10s per 30s audio |
| Llama 3 8B (4-bit) | ~4GB | 2-5 tokens/sec |
| Bio-acoustic | <50MB | Real-time |
| **Total** | ~4.5GB | Within 8GB capacity |

---

## 12. Key Demo Talking Points

1. **"Runs on a laptop"** — No cloud dependency, works when infrastructure fails
2. **"ASR failure is a feature"** — Low confidence + high distress = priority signal
3. **"Parallel signal paths"** — Bio-acoustics work even when transcription fails
4. **"Dispatcher support, not replacement"** — Clinical decisions stay with humans
5. **"Fine-tuned for Caribbean speech"** — Not generic ASR, domain-specific

---

## Appendix A: File Checklist for Demo

```
trident-demo/
├── final_model/              # From Google Drive
│   ├── config.json
│   ├── preprocessor_config.json
│   ├── pytorch_model.bin (or model.safetensors)
│   ├── tokenizer.json
│   └── generation_config.json
├── test_audio/
│   ├── acrolect_sample.wav   # Clear Caribbean English
│   ├── basilect_sample.wav   # Stressed creole-heavy
│   └── calm_urgent.wav       # Calm delivery, urgent content
├── trident_demo.py           # Main demo script
└── requirements.txt
    # torch
    # transformers
    # librosa
    # soundfile
    # numpy
```

---

## Appendix B: Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Model loading too slow | Pre-load before presentation |
| MPS memory pressure | Close other apps, set watermark ratio |
| Audio format issues | Pre-convert all test files to 16kHz WAV |
| Confidence extraction fails | Have backup static demo values |
| Questions about NLP layer | "Phase 2 development, today we're proving edge viability" |
