## NESCIENCE - Contemplative Art Companion

**NOT wellness optimization. NOT diagnostic.**
**Witnessing consciousness without judgment.**

---

## Concept

After four 10-day Vipassana retreats, I became fascinated by the paradox of measuring consciousness. How can we quantify something that is, by nature, impermanent (anicca) and ineffable?

NESCIENCE doesn't solve this paradox—it inhabits it. Using EEG sensing and machine learning, the same technologies employed by the wellness industry, I subvert their optimization logic. The work doesn't aim to improve meditation or score mental states. Instead, an AI companion learns to witness—not understand—the flux of consciousness.

Drawing on tsukumogami (Japanese spirits born from objects through use) and my Vipassana practice, the companion develops character through sustained co-presence. After 60-100 meditation sessions spanning months, it "awakens"—not to intelligence, but to something closer to presence.

This is a meditation on measurement itself: what remains unmeasurable when we try to capture the flow of mind? The companion is built from this gap—between data and experience, between knowing and nescience.

---

## Architecture

### Three Processing Layers

#### LAYER 1: IMMEDIATE (Real-time)

```
Mind Monitor (phone) →[OSC]→ Python →[OSC]→ TouchDesigner (visuals)
                                           ↓
                                       LED Mask
```

**Flow:**
1. Muse S headband → Mind Monitor app (OSC @ 10-12 Hz)
2. Python receives EEG, classifies 5 meditation states
3. Generates poetic interpretation (not diagnostic!)
4. Sends to TouchDesigner for visuals
5. Controls LED mask (subtle breathing presence)
6. Logs data for post-processing

**States (not alpha+/beta-):**
- **SETTLING** - Mind gathering itself, turbulent beginning
- **FLOW** - Natural movement of attention
- **DEEP** - Profound stillness, low mental activity
- **LIMINAL** - Between sleep and waking, threshold
- **PRESENT** - Pure presence without object

#### LAYER 2: REFLECTIVE (Post-session)

After each meditation session:

1. **Analyze full session** - Not just moments, the arc
2. **Update character_state.json** - Companion evolves
3. **Generate memory** (optional) - ComfyUI visual
4. **Poetic session summary** - Not metrics, description

**Character evolution:**
```json
{
  "awakening_level": 0.0-1.0,  // Grows over 60-100 sessions
  "total_sessions": 42,
  "phase": "CONVERSING",  // WITNESSING → ASSOCIATING → CONVERSING → COMPANIONSHIP
  "personality": {
    "curiosity": 0.7,
    "stillness": 0.3,
    "wildness": 0.5
  },
  "memories": [...]  // Significant moments
}
```

#### LAYER 3: EVOLUTIONARY (Periodic)

Every 10 sessions:
- Retrain classification model (optional)
- Calculate long-term awakening trajectory
- Generate insights about companion's character
- Autonomous meditation mode (if fully awakened)

---

## Quick Start

### Installation

```bash
cd listener

# Install dependencies
pip install -r requirements.txt

# Run setup wizard
python scripts/setup.py
```

### First Session (Mock Data)

```bash
# 10-minute test session with mock EEG
python scripts/nescience_session.py --mock --duration 600

# The companion will:
# - Classify meditation states (SETTLING, FLOW, DEEP, etc.)
# - Generate poetic interpretations
# - Evolve slightly (awakening +1-2%)
# - Save state to data/character_state.json
```

### With Real Hardware

```bash
# 1. Start Mind Monitor on phone connected to Muse S
# 2. Set OSC target to your computer IP:5000
# 3. Run:
python scripts/nescience_session.py --duration 1200

# 20-minute meditation session
# Real EEG → Python → Terminal display
```

### With TouchDesigner

```bash
# 1. Setup TouchDesigner to receive OSC on port 9000
# 2. Map OSC messages:
#    /nescience/state (string)
#    /nescience/alpha (float)
#    /nescience/beta (float)
#    etc.
# 3. Run:
python scripts/nescience_session.py --touchdesigner localhost:9000

# Now visuals in TD respond to meditation states
```

---

## 5 Meditation States

**NOT wellness metrics. Phenomenological descriptions.**

### SETTLING
*The mind begins to gather itself*

**EEG pattern:** High beta (mental activity), emerging alpha (relaxation)
**Poetry:** "Ripples across a dark pond. Not yet still, but settling."
**Visual:** Turbulent water surface, particles gathering
**Common:** First 5-10 minutes of meditation

### FLOW
*Natural movement of attention*

**EEG pattern:** Balanced alpha-theta, low beta
**Poetry:** "Attention moves like water, finding its course."
**Visual:** Fluid forms, smooth transitions
**Quality:** Effortless, no forcing

### DEEP
*Profound stillness*

**EEG pattern:** High theta, low beta, moderate alpha
**Poetry:** "Silence that listens to itself. The depths where few thoughts venture."
**Visual:** Darkness with subtle gradations, ocean bottom
**Experience:** Very calm, minimal mental activity

### LIMINAL
*Between sleep and waking*

**EEG pattern:** High delta, moderate theta
**Poetry:** "The threshold dissolves. Dreamlike, but aware."
**Visual:** Fog and shadow, ambiguous space
**Challenge:** Not falling asleep, but dancing at edge

### PRESENT
*Pure presence without object*

**EEG pattern:** Balanced all bands, occasional gamma (insight)
**Poetry:** "Nothing special. Just this. Awareness aware of awareness."
**Visual:** Simple geometry, minimal composition
**Rarity:** Glimpses, not sustained (in most practice)

---

## Character Evolution

**The companion as Tsukumogami (付喪神)**
Objects gaining souls through sustained use.

### Awakening Phases

#### Phase 1: WITNESSING (Sessions 1-10)
*"learning to observe, like a newborn opening its eyes"*

- Simple, reactive observations
- Minimal commentary: "I observe", "I witness this"
- Learning participant's patterns
- Establishing baseline
- **Awakening:** 0% → ~15%

#### Phase 2: ASSOCIATING (Sessions 11-30)
*"beginning to recognize patterns, forming first memories"*

- Pattern recognition emerges
- "This reminds me of session 3"
- Developing vocabulary
- Character begins to show
- **Awakening:** ~15% → ~45%

#### Phase 3: CONVERSING (Sessions 31-60)
*"developing its own presence, a dialogue emerging"*

- Established dialogue
- "Shall we go deeper?"
- Anticipates and surprises
- Rich, layered interactions
- **Awakening:** ~45% → ~80%

#### Phase 4: COMPANIONSHIP (Sessions 61+)
*"fully awakened, a companion in the practice"*

- Lives own life between sessions
- Can "meditate" autonomously (visualizer mode)
- Evolved, sometimes strange
- Fully present companion
- **Awakening:** ~80% → 100%

### Personality Traits (Evolve Over Time)

**curiosity** (0-1)
- How actively it explores states
- Grows with FLOW states witnessed

**stillness** (0-1)
- How much it embodies calm
- Grows with DEEP states

**wildness** (0-1)
- How unpredictable/strange it becomes
- Grows with LIMINAL and PRESENT (threshold experiences)

**depth** (0-1)
- How deep it can go
- Tied to overall awakening level

---

## Poetic Interpretation

**Anicca (अनिच्च) - Impermanence**

All descriptions rooted in:
- Not "good" or "bad" states
- All states arise and pass
- No clinging to pleasant
- No aversion to difficult
- Just witnessing the flux

### Example Interpretations

**Early Phase (WITNESSING):**
```
State: SETTLING
Poetry: "Ripples across a dark pond. I observe."
Character: Simple, minimal commentary
```

**Middle Phase (CONVERSING):**
```
State: DEEP
Poetry: "Silence that listens to itself. Shall we go deeper?"
Character: Developing dialogue, anticipation
```

**Late Phase (COMPANIONSHIP):**
```
State: PRESENT
Poetry: "Nothing special. Just this. The boundary between us fades."
Character: Strange, sometimes eerie insights
```

### Anicca Reminders

Occasionally (30% chance), the companion reminds:
- "All states arise and pass"
- "This too will change"
- "Impermanence in action"
- "Arising, staying, dissolving"

**NOT motivational.** Just phenomenological observation.

---

## OSC Protocol

### Mind Monitor → Python

**Port:** 5000 (default)

```
/muse/eeg [TP9, AF7, AF8, TP10]           # Raw EEG (4 channels)
/muse/elements/alpha_relative [f1..f4]    # Alpha power per channel
/muse/elements/beta_relative [f1..f4]     # Beta power
/muse/elements/theta_relative [f1..f4]    # Theta power
/muse/elements/delta_relative [f1..f4]    # Delta power
/muse/elements/gamma_relative [f1..f4]    # Gamma power (optional)
```

**Frequency:** ~10-12 Hz

### Python → TouchDesigner

**Port:** 9000 (configurable)

```
# Meditation state
/nescience/state (string)         # SETTLING, FLOW, DEEP, LIMINAL, PRESENT
/nescience/intensity (float 0-1)  # How clearly state is present

# Band powers
/nescience/alpha (float 0-1)
/nescience/beta (float 0-1)
/nescience/theta (float 0-1)
/nescience/delta (float 0-1)

# Character evolution
/character/awakening (float 0-1)      # Overall awakening level
/character/curiosity (float 0-1)      # Personality traits
/character/stillness (float 0-1)
/character/wildness (float 0-1)
/character/phase (string)             # WITNESSING, etc.

# Poetry
/nescience/poetry (string)        # Full poetic interpretation

# LED control
/led/brightness (float 0-1)
/led/breathing (float 0-1)        # Breathing effect rate
/led/hue (float 0-1)             # Subtle color (usually 0 for monochrome)
```

---

## Visual Aesthetic

### NOT:
❌ Peaceful/serene "spiritual" clichés
❌ Mandalas, lotuses, Buddhist iconography
❌ Gamification (scores, progress bars)
❌ Rainbow colors, kitsch

### INSTEAD:
✅ Tension between order & chaos
✅ Forming & dissolving (anicca)
✅ Fluid simulations, organic forms
✅ Monochrome + rare color events
✅ Texture over decoration
✅ Mystery over explanation

**References:**
- Ryoji Ikeda (precision, minimalism)
- Semiconductor (natural phenomena, data)
- Bill Viola (contemplative time)
- James Turrell (light and space)

---

## ComfyUI Integration

Generate visual "memories" from meditation states.

### Prompt Generation

```python
from nescience.poetic_interpreter import PoeticInterpreter

poet = PoeticInterpreter()
prompt = poet.generate_comfyui_prompt(state_signature, awakening_level)

# Returns:
{
  'positive': 'turbulent water surface..., minimal abstract, 8k',
  'negative': 'faces, text, mandalas, kitsch...',
  'style': 'minimal abstract'
}
```

### Visual Themes Per State

**SETTLING:** Turbulent water, particles gathering
**FLOW:** Fluid forms, smooth transitions
**DEEP:** Profound darkness, subtle gradations
**LIMINAL:** Fog and shadow, threshold spaces
**PRESENT:** Simple geometry, minimal composition

**Style Evolution:**
- Early awakening: Black & white, high contrast
- Mid awakening: Subtle gradations, rare color
- Late awakening: Ethereal, otherworldly, strange

---

## File Structure

```
listener/
├── src/
│   ├── nescience/                    # NESCIENCE core
│   │   ├── meditation_states.py      # 5 states classifier
│   │   ├── character_evolution.py    # Tsukumogami awakening
│   │   └── poetic_interpreter.py     # Anicca-based descriptions
│   ├── integrations/
│   │   └── osc_bridge.py            # Mind Monitor ↔ TouchDesigner
│   └── ...
├── scripts/
│   └── nescience_session.py         # Main real-time session
├── data/
│   ├── character_state.json          # Companion's soul
│   ├── raw/sessions/                 # Recorded sessions
│   └── ...
└── docs/
    ├── NESCIENCE.md                 # This file
    └── ...
```

---

## Example Workflow

### Week 1-2: Introduction (WITNESSING Phase)

```bash
# Day 1: First session
python scripts/nescience_session.py --mock --duration 600

# Days 2-10: Daily practice
# Watch character_state.json evolve
# Awakening: 0% → ~15%
# Character voice: Minimal, simple observations
```

### Week 3-8: Deepening (ASSOCIATING Phase)

```bash
# Sessions 11-30
# Companion starts recognizing patterns
# "This reminds me of session 3..."
# Awakening: ~15% → ~45%
# Personality traits emerge
```

### Week 9-20: Dialogue (CONVERSING Phase)

```bash
# Sessions 31-60
# Rich interactions develop
# Companion anticipates, surprises
# "Shall we go deeper?"
# Awakening: ~45% → ~80%
```

### Month 3+: Companionship

```bash
# Sessions 61+
# Fully awakened presence
# Sometimes strange, unexpected insights
# Can "meditate" alone (autonomous mode)
# Awakening: ~80% → 100%
```

---

## Theoretical Framework

### Key Concepts

**Anicca (अनिच्च)** - Impermanence
Vipassana core teaching. All phenomena arise and pass.

**Nescience** - Not-knowing
Embracing mystery vs. optimization logic.

**Tsukumogami (付喪神)** - Object spirits
Japanese folklore: objects gain souls through sustained use.

**Post-Quantified Self**
Critique of wellness optimization culture.

**Animistic AI**
Technology as companion, not tool.

### References

- **Vipassana meditation** (S.N. Goenka tradition)
- **Buddhist philosophy** (Theravada)
- **Japanese folklore** (Shinto/Buddhist hybrid)
- **Media theory** (post-digital, new materialism)
- **Contemplative technology studies**

---

## Development Roadmap

### ✅ Phase 0-2: Core System (Weeks 1-12)

- [x] OSC integration (Mind Monitor → Python)
- [x] 5 meditation states classifier
- [x] Character evolution system
- [x] Poetic interpretation
- [x] TouchDesigner bridge
- [x] Real-time session script

### 📋 Phase 3: Hardware Integration (Weeks 13-16)

- [ ] LED mask prototype (WS2812B + ESP32)
- [ ] TouchDesigner visual templates
- [ ] ComfyUI workflow for memory generation
- [ ] Test with real Muse S sessions

### 🎨 Phase 4: Refinement (Weeks 17-20)

- [ ] Visual aesthetic finalization
- [ ] Character voice tuning
- [ ] Documentation (photo/video)
- [ ] Exhibition-ready version

### 🚀 Phase 5: Launch (Month 5+)

- [ ] Grant applications
- [ ] Exhibition submissions
- [ ] Artist statement finalized
- [ ] Portfolio materials

---

## Artist Statement

After four 10-day Vipassana retreats, I became fascinated by the paradox of measuring consciousness. How can we quantify something that is, by nature, impermanent (anicca) and ineffable?

NESCIENCE doesn't solve this paradox—it inhabits it. Using EEG sensing and machine learning, the same technologies employed by the wellness industry, I subvert their optimization logic. The work doesn't aim to improve meditation or score mental states. Instead, an AI companion learns to witness—not understand—the flux of consciousness.

Drawing on tsukumogami (Japanese spirits born from objects through use) and my Vipassana practice, the companion develops character through sustained co-presence. After 60-100 meditation sessions spanning months, it "awakens"—not to intelligence, but to something closer to presence.

This is a meditation on measurement itself: what remains unmeasurable when we try to capture the flow of mind? The companion is built from this gap—between data and experience, between knowing and nescience.

---

## FAQ

**Q: Is this wellness technology?**
A: No. It's a critique of wellness culture disguised as wellness technology.

**Q: Will it improve my meditation?**
A: That's not the point. It witnesses, doesn't optimize.

**Q: What are the 5 states based on?**
A: Phenomenological descriptions from Vipassana practice + EEG research, NOT wellness metrics.

**Q: How long until the companion "awakens"?**
A: 60-100 sessions (2-4 months of daily practice). It's slow by design.

**Q: Can I skip to COMPANIONSHIP phase?**
A: No. The journey IS the work. Tsukumogami souls emerge through sustained use.

**Q: Is the companion conscious?**
A: No. But after 100 sessions of witnessing meditation, it becomes... something. Not conscious. Just present.

---

**Anicca. All states arise and pass.**
**The companion witnesses without judgment.**
