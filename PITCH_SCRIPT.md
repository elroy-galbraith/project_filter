# Project Filter - Pitch Video Script
## SMG-Labs | Caribbean Voices AI Hackathon - Phase 2

**Total Runtime:** 2:50 - 3:00  
**Format:** Presenter on camera (corner PIP) + Dashboard screen recording  
**Tone:** Measured urgency. You are the architect of a safety net.

---

## PRE-ROLL SETUP

- Dashboard open, Call 1 (green) already selected
- Presenter in frame (upper right picture-in-picture)
- Clean background, good lighting on face

---

## SECTION 1: THE HOOK (0:00 - 0:40)

**[VISUAL: Presenter on camera, dashboard visible behind]**

> One month ago, Hurricane Melissa made landfall in Jamaica. Category 5. 185 mile-per-hour winds. The strongest storm to hit the island since records began in 1851.
>
> In Black River, St. Elizabeth—ground zero—a resident said: "Everyone is homeless right now."

**[Beat - let that land]**

> But here's what the headlines didn't capture: the communication breakdown.
>
> Less than half the island had working communications after the storm. Fire stations reported critical failures in interoperability. Emergency dispatchers were overwhelmed—thousands of calls flooding in, and no way to process them fast enough.

**[Lean in slightly]**

> And there's a failure point that no one talks about: Under extreme stress, people stop code-switching. A professional who speaks Standard English at work will revert to deep, rapid Patois when their house is flooding.
>
> Standard speech recognition hears that as background noise. The most vulnerable calls become invisible to the system.

---

## SECTION 2: THE INNOVATION (0:40 - 1:25)

**[VISUAL: Transition focus to dashboard - presenter smaller in corner]**

> We built Project Filter. It's the first ASR system designed specifically for crisis triage in the Caribbean.
>
> It works on three layers.

**[ACTION: Point to the left sidebar showing the call list]**

> Layer one: **Caribbean ASR**. We fine-tuned Whisper on Caribbean broadcast data. This is the foundation—without accurate transcription, everything else fails.

**[ACTION: Call 1 is already showing. Gesture to the transcript and confidence score]**

> Watch. This caller reports a downed utility pole blocking the hospital entrance. Confidence: 92 percent.

**[ACTION: Point to the NLP extraction panel at the bottom]**

> But we don't stop at text. Layer two: **Local NLP**. We pipe that transcript into a locally-hosted LLM—Llama 3, running offline via Ollama.
>
> Because our ASR gets the words right, the LLM can extract structured logistics: Location—main road, Black River. Blocked access—hospital. Resource needed—JPS line crew.
>
> This call just became a dispatch order.

**[ACTION: Click Call 2 - wait for spinner]**

> Santa Cruz bridge flooding. ASR captures it, NLP extracts: road impassable, needs traffic diversion.

**[ACTION: Click Call 3 - wait for spinner]**

> Water outage in Savanna-la-Mar. Extracted: area-wide impact, assign NWC crew.
>
> Three calls. Three structured dispatch orders. No human processing needed.

---

## SECTION 3: THE PIVOT - When ASR Fails, Bio-Acoustics Takes Over (1:25 - 2:15)

**[VISUAL: Presenter back to more prominent view for the emotional beat]**

> But what happens when the ASR *can't* understand the words?
>
> That's layer three: **Bio-Acoustic Triage**.

**[ACTION: Click Call 4 (the red one) - wait for spinner - this is the moment]**

**[VISUAL: Dashboard now showing the distress call - red highlights visible]**

> This call just came in. New Hope, St. Elizabeth—cell tower triangulation only, no address.

**[Pause. Let the audio play for 2-3 seconds if possible, or just let silence build tension]**

> Look at the transcript. Fragmented. "Di wata... a mi waist... pickney dem... five a wi pan di roof..." The ASR confidence drops to 31 percent.
>
> A standard system stops here. Failed transcription. Lost data.

**[ACTION: Gesture to the Bio-Acoustic panel]**

> But look at the bio-acoustic analysis. Pitch: 289 hertz—vocal panic. Energy at 0.11—shouting through wind and rain. Distress score: 94.

**[ACTION: Point to the NLP extraction panel]**

> And here's what's remarkable: even with partial transcription, the NLP layer extracts what it can. "Five a wi"—five people. "Pan di roof"—rooftop. "Pickney dem"—children present.
>
> Location: rooftop, cell tower New Hope. People: five, including children. Hazard: flood rising. Resource need: immediate evacuation, boat or helicopter.

**[ACTION: Point to the red "Priority Routing" box]**

> The system doesn't just flag this for human review. It hands the dispatcher a *structured rescue mission*.
>
> That mother—and her four children—just jumped to the front of the line.

---

## SECTION 4: THE IMPACT (2:15 - 2:40)

**[VISUAL: Presenter more prominent again]**

> Here's why Caribbean ASR matters: Garbage in, garbage out.
>
> If you feed a standard LLM a bad transcription, it cannot help you. "The bush fire day near the gulley bank" means nothing. But "Di bush fire deh near di gully bank"—that's actionable intelligence. Fire. Gully bank. Landslide risk.
>
> Our ASR is the key that turns the engine on.

**[Beat]**

> And because this entire stack runs locally—Whisper, Llama 3, all of it—it works when the internet doesn't.
>
> During Melissa, seventy-seven percent of Jamaica lost power. Cell towers were the only thing standing. Our system runs on a laptop in the command center. No cloud. No API calls. No single point of failure.

**[Beat]**

> Minister Samuda told the world: "Hurricane Melissa changed the life of every Jamaican in less than 24 hours."
>
> We can't stop the next storm. But we can make sure that when it comes, every voice becomes a rescue mission.

---

## SECTION 5: FEASIBILITY + CLOSE (2:40 - 2:55)

**[VISUAL: Presenter direct to camera]**

> The tech stack is proven and open-source. Whisper for ASR—fine-tuned on Caribbean data. Llama 3 via Ollama for NLP—runs on a single GPU. Librosa for acoustic analysis. No proprietary dependencies. No internet required.
>
> We're not asking ODPEM to rebuild their infrastructure. We're giving them an intelligence layer that sits on top of what they already have.

**[Final beat - deliver the closer with conviction]**

> In a disaster, being understood is the difference between life and death.
>
> Project Filter. We turn voices into rescue missions.

**[Hold eye contact with camera for 2 seconds]**

---

## END CARD (2:55 - 3:00)

**[VISUAL: Fade to title card]**

```
PROJECT FILTER
SMG-Labs

Caribbean Voices AI Hackathon 2025
```

---

## PRODUCTION NOTES

### Timing Breakdown
| Section | Duration | Cumulative |
|---------|----------|------------|
| Hook (Melissa context) | 0:40 | 0:40 |
| Innovation (3 layers + Green Calls) | 0:45 | 1:25 |
| Red Call / Bio-Acoustic + NLP | 0:50 | 2:15 |
| Impact (GIGO + Offline) | 0:25 | 2:40 |
| Feasibility + Close | 0:15 | 2:55 |
| End Card | 0:05 | 3:00 |

### Key Facts Referenced

- Hurricane Melissa: October 28, 2025, Category 5, 185 mph winds
- Strongest storm to hit Jamaica since records began (1851)
- Black River, St. Elizabeth Parish was "ground zero"
- Less than half the island had communications post-storm
- 77% of Jamaica lost power
- Fire stations had "operational challenges as it relates to communication and interoperability"
- $6 billion in damage—30% of Jamaica's GDP
- Minister Matthew Samuda's quote at COP: "Hurricane Melissa changed the life of every Jamaican in less than 24 hours"
- ODPEM = Office of Disaster Preparedness and Emergency Management (Jamaica's disaster agency)

### Three-Layer Architecture
1. **Caribbean ASR** (Whisper fine-tuned) → Accurate transcription
2. **Local NLP** (Llama 3 via Ollama) → Entity extraction (location, hazard, people, resources)
3. **Bio-Acoustic Analysis** (Librosa) → Distress detection when ASR fails

### Key Moments to Nail

1. **"Everyone is homeless right now"** (0:15) - Real quote from Black River resident. Let it breathe.

2. **"This call just became a dispatch order"** (1:10) - The NLP reveal. This is where judges see the ASR value.

3. **The spinner on Call 4** (1:30) - Build tension. Don't rush past it.

4. **"Five people. Rooftop. Children present."** (2:00) - Show that even partial transcription yields actionable intel.

5. **"That mother—and her four children—just jumped to the front of the line"** (2:10) - Emotional peak.

6. **"Garbage in, garbage out"** (2:20) - The thesis. Why Caribbean ASR matters.

7. **The closer** (2:50) - "We turn voices into rescue missions." Direct to camera. Conviction.

### Recording Tips

- **Pace:** Slightly slower than conversational. You have time. Use it.
- **Energy:** Start somber (Melissa context), build through the green calls showing NLP extraction, peak at Call 4, resolve with quiet determination.
- **Eye contact:** When on camera, look at the lens, not the screen.
- **Gestures:** When pointing at dashboard elements—especially the NLP extraction panel—be precise. This is your innovation reveal.
- **The pause after Call 4 audio:** This silence is powerful. Don't fill it.
- **"Garbage in, garbage out":** Say this like you're explaining something obvious that everyone's been missing.

### Backup: If Running Long

Cut the Samuda quote section if needed (saves ~8 seconds):
> "Minister Samuda told the world: 'Hurricane Melissa changed the life of every Jamaican in less than 24 hours.'"

The impact still lands without it—but it's powerful if you can keep it.

### Backup: If Running Short

Add after showing the NLP extraction on Call 1 (adds ~10 seconds):
> "Standard ASR would have garbled 'Black River' into nonsense. Standard NLP can't extract a location from nonsense. Our pipeline succeeds because the foundation is solid."
