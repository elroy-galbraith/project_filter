# TRIDENT Live Pitch Preparation Guide
## Caribbean Voices AI Hackathon - Final Round (Dec 13, 2025)

---

## 🎯 Executive Summary

**Congratulations on making the live pitch finals!** You're pitching to decision-makers (CEOs/CFOs) at the UWI AI Innovation Centre launch. Your 3 minutes must secure buy-in, not just explain tech.

**Your Core Advantage:** TRIDENT isn't just a speech recognition solution—it's a **dispatcher-support system** that turns ASR's biggest weakness (failing on Caribbean accents under stress) into a **triage signal**. This insight is genuinely novel.

---

## 📊 Scoring Alignment Analysis

| Criteria | Weight | Your Current Strengths | Gaps to Address |
|----------|--------|----------------------|-----------------|
| **Innovation** | 40% | ✅ Novel "failure-as-feature" insight, ✅ Bio-acoustic distress layer, ✅ Three-layer redundancy | Need to emphasize uniqueness vs. existing emergency AI |
| **Impact** | 40% | ✅ Hurricane Melissa hook (recent, real), ✅ 40M+ Caribbean population, ✅ ESI/START protocol alignment | Strengthen scalability pitch across islands |
| **Feasibility** | 20% | ✅ Offline operation, ✅ Edge deployment (RPi5), ✅ Existing component tech | Clarify MVP timeline and pilot pathway |

---

## ⏱️ Recommended 3-Minute Structure

### **0:00-0:30 — The Hook (30 sec)**
*Goal: Emotional connection + problem framing*

**Suggested Script:**
> "Two months ago, Hurricane Melissa hit Jamaica—the strongest storm in recorded history. In Black River, St. Elizabeth, a resident said: 'Everyone is homeless right now.'
>
> But the headlines missed something: the communication breakdown. Under extreme stress, a professional who speaks Standard English at work reverts to deep, rapid Patois—exactly when they need help most. Standard AI hears that as noise. Their accent becomes an accident."

**Why this works:** Real, recent, visceral. Decision-makers remember stories, not specs.

---

### **0:30-1:30 — The Solution (60 sec)**
*Goal: Demonstrate innovation WITHOUT getting lost in technical details*

**Key Pivot:** Don't present three layers as a list. Present the **insight** first, then show how layers implement it.

**Suggested Script:**
> "TRIDENT flips the problem. When AI struggles to understand a caller AND detects elevated vocal stress, that's not a failure—it's a signal that someone in crisis needs human attention NOW.
>
> We built three complementary signals:
> 1. **Caribbean-tuned ASR** that actually works on our accents—fine-tuned on 28,000 BBC Caribbean clips
> 2. **Local NLP** that extracts location, hazard, and casualties—even from imperfect transcripts
> 3. **Bio-acoustics** that detects panic in pitch and volume—no words needed
>
> A composed first responder calmly reporting 'children trapped in burning building' gets priority from the content. A panicked grandmother whose speech AI can't parse gets priority from her voice. Neither falls through the cracks."

---

### **1:30-2:15 — Impact & Scalability (45 sec)**
*Goal: Make it about the Caribbean, not just Jamaica*

**Suggested Script:**
> "TRIDENT doesn't replace triage protocols—it helps dispatchers apply Jamaica's existing ESI and START protocols faster and more fairly.
>
> This works for any emergency call center in the Caribbean: Trinidad, Barbados, Guyana—anywhere our voices are currently invisible to AI. Forty million Caribbean people deserve technology that understands them.
>
> And it runs on a laptop. No cloud, no API calls. When the next hurricane takes down cell towers, a unit at a shelter keeps working."

---

### **2:15-2:50 — Feasibility & Ask (35 sec)**
*Goal: Concrete MVP, clear next step*

**Suggested Script:**
> "The components exist today. Whisper fine-tuning works—we proved that in this hackathon. Bio-acoustic stress detection is validated science. We need six months and one pilot site—one island emergency operations center willing to test queue prioritization during the next surge event.
>
> Our ask: connect us to a Ministry of Health partner ready to deploy this before next hurricane season."

---

### **2:50-3:00 — Close (10 sec)**
*Goal: Memorable tagline*

> "We can't stop the next storm. But we can make sure every voice becomes a rescue mission. Help us ensure no accent becomes an accident."

---

## 🎤 Speaker Notes for Each Slide

Based on your current deck, here's how to map the script to slides:

| Slide | Content | Timing | Key Verbal Emphasis |
|-------|---------|--------|-------------------|
| 1 | Title: TRIDENT | 0:00-0:05 | "SMG Labs presents TRIDENT" |
| 2 | Hurricane Melissa before/after | 0:05-0:30 | Hit the emotional beat hard |
| 3 | Communication breakdown | 0:30-0:50 | "Accent becomes accident" - pause here |
| 4 | TRIDENT introduction | 0:50-1:00 | Quick transition, explain acronym briefly |
| 5 | Layer 1: Tuned ASR | 1:00-1:10 | "Fine-tuned on YOUR data" |
| 6 | Layer 2: Local NLP | 1:10-1:20 | "Works even on imperfect transcripts" |
| 7 | Layer 3: Bio-Acoustics | 1:20-1:30 | "Your voice tells the truth your words can't" |
| 8 | Core Insight | 1:30-1:45 | **PAUSE AND LAND THIS** - it's your differentiator |
| 9 | Impact/Feasibility | 1:45-2:30 | Show breadth, mention offline operation |
| 10 | Call to Action | 2:30-2:50 | Direct ask for pilot partnership |
| 11 | Thank You | 2:50-3:00 | "No accent becomes an accident" |

---

## ❓ Anticipated Q&A Questions

### Innovation Questions (40% weight)
**Q: How is this different from existing emergency AI like Corti or ECA?**
> "They process text only and assume clean transcription. They're cloud-dependent. They don't account for dialect shift under stress. TRIDENT is the first system designed for the 40% of humanity whose accents current ASR fails on."

**Q: Is the 'failure-as-feature' concept validated?**
> "The underlying science is solid—psycholinguistic research confirms stress causes code-switching, and acoustic studies confirm vocal markers elevate under crisis. What's new is combining these into a triage signal. Empirical validation on Caribbean emergency calls is our next milestone."

**Q: Why not just make better ASR instead of this workaround?**
> "Better ASR is necessary but not sufficient. Madden et al. achieved 30% WER on Jamaican Patois—dramatic improvement, still 6x worse than standard English. And that's on broadcast speech, not emergency calls with noise and panic. We need systems robust to ASR imperfection, not dependent on perfection."

### Impact Questions (40% weight)
**Q: How does this help marginalized communities specifically?**
> "The creole continuum means speakers with less formal education—rural communities, elderly callers, those under extreme stress—shift furthest from Standard English. Current AI deprioritizes them systematically. TRIDENT treats that shift as a priority signal instead."

**Q: Can this scale beyond Jamaica?**
> "The architecture is Caribbean-universal. Different islands have different creole varieties, but the pattern holds: stress causes dialect shift. We'd need island-specific ASR fine-tuning, but the bio-acoustic layer works across all English-lexified creoles."

**Q: What's the potential lives-saved impact?**
> "During Hurricane Maria, Puerto Rico's communication failure contributed to an estimated 3,000 excess deaths. We can't claim specific numbers, but queue prioritization during surge events—getting the most critical calls to dispatchers first—has direct impact on response times."

### Feasibility Questions (20% weight)
**Q: What's your MVP?**
> "A standalone queue prioritization module that integrates with existing CAD systems. Incoming audio gets scored for priority; dispatchers see calls in priority order with confidence flags. No changes to clinical protocols—just better information, faster."

**Q: What hardware do you need?**
> "Raspberry Pi 5 with 8GB RAM runs the entire stack. Total footprint under 5GB. No cloud, no API calls. Power it with a battery backup at a shelter and it survives grid failure."

**Q: What's the timeline to deployment?**
> "Six months to MVP with a pilot site. Phase 1: integrate with one emergency ops center for queue testing. Phase 2: collect data to validate prioritization accuracy. Phase 3: expand to additional islands."

**Q: What are the biggest risks?**
> "Training data gap is primary—Caribbean emergency speech corpora don't exist. We're designing VoicefallJA, a gamified data collection platform. Secondary risk is institutional adoption; we need Ministry of Health buy-in. That's our ask today."

---

## 🎯 Key Phrases to Land

Use these phrases deliberately throughout your pitch:

1. **"No accent becomes an accident"** — Your tagline. Say it at least twice.
2. **"Failure as a feature"** — The insight that makes TRIDENT unique
3. **"Forty million Caribbean voices"** — Scale the impact
4. **"No cloud, no API calls"** — Differentiator for disaster resilience
5. **"Supports dispatchers, doesn't replace them"** — Addresses AI skepticism
6. **"ESI and START protocols"** — Shows you understand clinical reality

---

## ⚠️ Things to Avoid

- **Don't get lost in layer details.** You have 3 minutes. The three layers are a means, not the message.
- **Don't oversell unvalidated claims.** Your paper is honest about the validation gap. Stay honest in the pitch.
- **Don't make it only about Jamaica.** The judges represent the broader Caribbean. Make it regional.
- **Don't use jargon with decision-makers.** "Basilectal register" → "deep Patois." "F0 elevation" → "pitch changes when you're panicked."
- **Don't forget the ask.** End with a specific request: pilot partnership, ministry introduction, something concrete.

---

## 🔧 Technical Backup (If Asked)

Keep these stats ready but don't volunteer them unless asked:

| Component | Spec | Source |
|-----------|------|--------|
| ASR WER on Patois | 30% (fine-tuned) vs 89% (baseline) | Madden et al. 2025 |
| Vocal stress F0 change | +62% during life-threatening emergencies | Van Puyvelde et al. 2018 |
| Edge hardware | Raspberry Pi 5, 8GB RAM, 4.5GB total | Your architecture |
| Processing latency | 45-60 sec full pipeline, 12 sec early exit | Your architecture |
| Target population | 40M+ Caribbean English speakers | Demographics |

---

## 🎬 Demo Recommendation

If you can show a demo within time limits, the **highest-impact moment** would be:

1. Play a short audio clip of stressed Caribbean speech
2. Show the three scores appearing: ASR confidence (low), bio-acoustic distress (high), queue priority (Q1-IMMEDIATE)
3. Show the dispatcher interface flagging it for human review

This visualizes the "failure-as-feature" insight better than any explanation.

If no demo, consider playing just 5-10 seconds of audio to make the problem visceral, then describe what TRIDENT would do.

---

## 📋 Pre-Pitch Checklist

- [ ] Test internet connection (wired if possible)
- [ ] Quiet environment confirmed
- [ ] Slides loaded and tested
- [ ] Demo ready (if using)
- [ ] Backup slides on phone/tablet
- [ ] Timer visible during pitch
- [ ] Water available
- [ ] Chad and Donahue briefed on Q&A topics
- [ ] One designated lead presenter

---

## 💪 Final Confidence Note

You built something genuinely novel. The "failure-as-feature" insight is the kind of reframe that wins competitions because it shows deep thinking, not just coding skill. Your paper demonstrates you understand the clinical context (ESI/START), the linguistic reality (creole continuum), and the deployment constraints (disaster resilience).

You're not pitching a prototype—you're pitching a framework for Caribbean emergency AI. Own that.

Good luck! 🔱
