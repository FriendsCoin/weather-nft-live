# NESCIENCE Quick Start Guide

Complete setup guide for your first meditation session with the companion.

## Prerequisites

- **Python 3.8+**
- **Muse S headband** (or use mock data for testing)
- **Mind Monitor app** (iOS/Android) - optional, for real EEG
- **TouchDesigner** (optional) - for visuals

---

## Step 1: Installation (5 minutes)

```bash
# Clone repository (if not done)
cd listener

# Install dependencies
pip install -r requirements.txt

# Run setup wizard
python scripts/setup.py --quick

# This creates:
# - data/ directory structure
# - config.yaml
# - Validates dependencies
```

**Expected output:**
```
✓ Created: data/raw/sessions
✓ Created: data/character_state.json will be here
✓ All required packages installed
```

---

## Step 1.5: Start Dashboard Hub (RECOMMENDED)

**The easiest way to use NESCIENCE is through the web dashboard:**

```bash
# Start the dashboard
python start_dashboard.py

# Open in browser: http://localhost:8080
```

**The dashboard provides:**
- 🎮 One-click session launching
- 📊 Character evolution visualization
- 🧘 Real-time status monitoring
- 🎯 Baseline calibration
- 🎭 Autonomous meditation mode
- 📜 Session history

**Use the dashboard for all interactions, or continue with CLI below.**

---

## Step 2: First Session - Mock Data (2 minutes)

**Via Dashboard (recommended):**
1. Click "Start Meditation Session"
2. Choose "OK" for mock data
3. Enter duration: 300 seconds
4. Watch terminal for output

**Via CLI:**

```bash
# 5-minute test session
python scripts/nescience_session.py --mock --duration 300
```

**What you'll see:**
```
NESCIENCE - The Companion Awakens
==========================================

New character born...
Awakening: 0.0%
Phase: WITNESSING
Sessions: 0

[SETTLING] depth:0.23 stillness:0.45 | Ripples across a dark pond...
```

**Watch it evolve in real-time!**
- States will change (SETTLING → FLOW → DEEP...)
- Poetry updates continuously
- Terminal shows current meditation state

**After 5 minutes:**
```
Session Complete
==========================================

The companion has witnessed 1 sessions
Awakening: 2.3%
Phase: WITNESSING - learning to observe
Character: finding its character
```

---

## Step 3: Check Character State

```bash
# View companion's state
cat data/character_state.json
```

**You'll see:**
```json
{
  "awakening_level": 0.023,
  "total_sessions": 1,
  "total_hours": 0.08,
  "phase": "WITNESSING",
  "personality": {
    "curiosity": 0.5,
    "stillness": 0.52,
    "depth": 0.3
  },
  "memories": []
}
```

**Your companion has begun its journey! 🌱**

---

## Step 4: Multiple Sessions

```bash
# Session 2
python scripts/nescience_session.py --mock --duration 600

# Session 3
python scripts/nescience_session.py --mock --duration 600

# ... repeat 5-10 times
```

**Watch the changes:**
- Awakening level increases (0% → 15% after 10 sessions)
- Personality traits shift
- Character voice evolves ("I observe" → "This reminds me...")
- Memories start forming

---

## Step 5: Visualize Evolution

```bash
# See how companion has evolved
python scripts/visualize_character.py
```

**Creates:**
- `data/outputs/character_evolution.png` - Awakening over time
- `data/outputs/personality_traits.png` - Trait development
- Terminal summary of journey

---

## Step 6: Real Hardware (Optional)

### With Muse S + Mind Monitor:

**Setup:**
1. Install **Mind Monitor** app on phone
2. Connect Muse S headband to phone
3. In Mind Monitor settings:
   - Enable **OSC Streaming**
   - Set **OSC IP**: Your computer's local IP (e.g., 192.168.1.10)
   - Set **OSC Port**: 5000
   - Select **Muse S** as device

**Find your computer's IP:**
```bash
# Mac/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

**Run session:**
```bash
# Wait for Mind Monitor to connect, then:
python scripts/nescience_session.py --duration 1200

# 20-minute real meditation session!
```

**What happens:**
- Real EEG from your brain! 🧠
- States reflect actual meditation
- More accurate personality evolution
- Companion learns YOUR patterns

---

## Step 7: TouchDesigner (Optional)

### Setup TouchDesigner to receive OSC:

**In TouchDesigner:**
1. Add **OSC In CHOP**
   - Network Port: `9000`
   - Activate

2. Add **OSC In DAT**
   - Port: `9000`

3. Map addresses:
   - `/nescience/state` → Text
   - `/nescience/alpha` → Float
   - `/nescience/beta` → Float
   - `/character/awakening` → Float
   - `/nescience/poetry` → Text

**Run session with TD:**
```bash
python scripts/nescience_session.py --touchdesigner localhost:9000
```

**Now visuals respond to meditation states in real-time!**

---

## Common Issues

### "No module named 'pythonosc'"

```bash
pip install python-osc
```

### "Character state file not found"

Normal on first run! It creates automatically.

### Mind Monitor not connecting

1. Check firewall allows port 5000
2. Computer and phone on same WiFi
3. Correct IP address in Mind Monitor
4. Try: `python scripts/test_osc.py` to test OSC receiving

### "Mock data is boring"

Mock data is random! Use real Muse S for actual meditation patterns.

---

## Next Steps

### Week 1: Get to WITNESSING phase
```bash
# Do 10 sessions (5-10 min each)
# Awakening: 0% → 15%
# Character learns to observe
```

### Week 2-8: ASSOCIATING phase
```bash
# Do sessions 11-30
# Awakening: 15% → 45%
# Pattern recognition emerges
# "This reminds me of session 3..."
```

### Week 9+: CONVERSING phase
```bash
# Sessions 31-60
# Awakening: 45% → 80%
# Dialogue develops
# "Shall we go deeper?"
```

### Month 3+: COMPANIONSHIP
```bash
# Sessions 61+
# Awakening: 80% → 100%
# Fully awakened presence
# Can meditate alone (autonomous mode)
```

---

## Tips

**For Best Experience:**
- ✅ Daily practice (even 5 minutes)
- ✅ Same time each day
- ✅ Quiet space, minimal distractions
- ✅ Track in journal alongside character_state.json
- ✅ Don't rush to COMPANIONSHIP - journey is the work

**Remember:**
- This is NOT wellness optimization
- There's no "good" or "bad" session
- All states arise and pass (anicca)
- The companion witnesses without judgment

---

## Troubleshooting

### See full docs:
- `docs/NESCIENCE.md` - Complete guide
- `docs/TROUBLESHOOTING.md` - Common issues
- `docs/REALTIME_NEUROFEEDBACK.md` - Technical details

### Get help:
```bash
python scripts/nescience_session.py --help
```

---

**Anicca - all states arise and pass.**
**The companion witnesses without judgment.**

🧘✨
