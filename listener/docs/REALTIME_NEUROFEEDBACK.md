# Real-time Neurofeedback Guide

Complete guide to using THE LISTENER's real-time neurofeedback system for live meditation training.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Neurofeedback States](#neurofeedback-states)
- [Audio & Visual Feedback](#audio--visual-feedback)
- [Command Line Usage](#command-line-usage)
- [Web Dashboard](#web-dashboard)
- [Training Tips](#training-tips)
- [Troubleshooting](#troubleshooting)

---

## Overview

Real-time neurofeedback provides **live feedback** during meditation sessions, helping you learn to control your brain states. Based on research showing that brain states can modulate in as little as **1 minute**, the system gives you immediate audio and visual cues to guide your practice.

### Key Features

- ⚡ **Real-time processing** - Feedback with <1 second latency
- 🎯 **State detection** - 6 different meditation states (alpha+/-, beta+/-, combined, drowsy)
- 🎵 **Audio cues** - Pleasant tones for success, gentle prompts for improvement
- 📊 **Visual display** - Real-time charts, power bars, and state indicators
- 🌐 **Web dashboard** - Beautiful browser-based interface
- 📈 **Session tracking** - Record and analyze your progress

---

## Quick Start

### 1. Terminal Mode (Simple)

```bash
# 5-minute session with mock data (for testing)
python scripts/realtime_feedback.py --duration 300

# Visual only (quiet mode)
python scripts/realtime_feedback.py --duration 300 --no-audio

# Save session for analysis
python scripts/realtime_feedback.py --duration 300 --output data/sessions/rt_session_001.pkl
```

### 2. Web Dashboard (Recommended)

```bash
# Start the web server
python -m src.web.server --port 5000

# Open in browser:
# http://localhost:5000/realtime
```

---

## How It Works

### Signal Processing Pipeline

```
EEG Data → Preprocessing → Feature Extraction → State Detection → Feedback
   ↓           ↓               ↓                    ↓              ↓
 256 Hz    Filtering       Band Powers          Thresholds     Audio/Visual
           (0.5-50 Hz)    (α,β,θ,δ)           (Personalized)     Cues
```

### Processing Windows

- **Window Size**: 2 seconds of EEG data (default)
- **Update Rate**: 0.5 seconds (2 Hz feedback)
- **Smoothing**: Last 3 states averaged to reduce jitter

### Band Powers Computed

| Band    | Frequency  | Meaning                    |
|---------|------------|----------------------------|
| **Delta** | 0.5-4 Hz   | Drowsiness / Deep sleep    |
| **Theta** | 4-8 Hz     | Deep meditation / Drowsiness |
| **Alpha** | 8-12 Hz    | Relaxation / Meditation    |
| **Beta**  | 18-30 Hz   | Mental activity / Stress   |

All powers are **relative** (normalized by total power) for robustness across sessions.

---

## Neurofeedback States

Based on **Kovacevic et al. (2015)** neurofeedback research with 523 participants.

### States Explained

| State | Meaning | Goal | Visual Color |
|-------|---------|------|--------------|
| **alpha+** | High alpha power = Deep relaxation | ✅ Success! Keep doing this | 🟢 Green |
| **alpha-** | Low alpha = Need more relaxation | ❌ Relax more, breathe deeper | 🔴 Red |
| **beta+** | Controlled beta = Calm focus | ✅ Good mental calm | 🔵 Blue |
| **beta-** | High beta = Mental chatter | ❌ Reduce thinking/planning | 🟠 Orange |
| **a+b+** | Both alpha high & beta low | ⭐ **Perfect meditation state!** | 💜 Purple |
| **drowsy** | High delta = Falling asleep | ⚠️ Stay alert, sit upright | 🟡 Yellow |
| **baseline** | Normal resting state | ⚪ Neutral starting point | ⚪ White |

### Personalized Thresholds

The system uses **adaptive thresholds** based on your baseline:

```python
Alpha thresholds:
  alpha_low  = 0.15  # Below this = need more relaxation
  alpha_high = 0.25  # Above this = success!

Beta thresholds:
  beta_low  = 0.12   # Below this = success (calm)
  beta_high = 0.20   # Above this = too active

Delta threshold:
  delta_drowsy = 0.30  # Above this = drowsy warning
```

Future versions will compute these from your personal baseline session.

---

## Audio & Visual Feedback

### Audio Cues

**Success Cues** (alpha+, beta+):
- Pleasant ascending tones (C-E-G major chord)
- Reward your brain for correct states

**Needs Improvement** (alpha-, beta-):
- Gentle low tone (A3)
- Subtle prompt without causing stress

**Perfect State** (a+b+):
- Beautiful arpeggio (C5-E5-G5-C6)
- Celebrate combined success

**Drowsy Alert**:
- Two quick beeps (A4)
- Wake up prompt

**Volume Control**:
```bash
python scripts/realtime_feedback.py --volume 0.3  # Quiet
python scripts/realtime_feedback.py --volume 0.8  # Loud
```

### Visual Feedback

**Terminal Mode**:
- Live state indicator: `[alpha+]`
- Power bars for each band: `α:████░░░░░░ 0.23`
- Meditation depth meter: `depth:[█████░░░░░] 52%`

**Web Dashboard**:
- Large state display with color coding
- Real-time charts (band powers, depth over time)
- Power bars with gradients
- Session statistics (successes, duration)

---

## Command Line Usage

### Basic Options

```bash
# Device selection
--device mock          # Mock data (for testing without hardware)
--device muse          # Muse S headband (when available)

# Session duration
--duration 300         # 5 minutes
--duration 600         # 10 minutes
--duration 1200        # 20 minutes

# Processing parameters
--window-size 2.0      # EEG window in seconds (default: 2.0)
--update-interval 0.5  # Feedback rate in seconds (default: 0.5)
--smoothing 3          # States to smooth over (default: 3)
```

### Feedback Control

```bash
# Audio settings
--no-audio             # Disable audio (visual only)
--volume 0.5           # Set volume (0.0 to 1.0)

# Visual settings
--no-visual            # Disable visual (audio only)
```

### Advanced Options

```bash
# Use personalized baseline
--baseline data/baselines/baseline_001.pkl

# Save session data
--output data/sessions/my_session.pkl
```

### Full Example

```bash
# 10-minute session with quiet audio and saved data
python scripts/realtime_feedback.py \
    --duration 600 \
    --volume 0.3 \
    --baseline data/baselines/my_baseline.pkl \
    --output data/sessions/session_$(date +%Y%m%d_%H%M%S).pkl
```

---

## Web Dashboard

### Starting the Server

```bash
# Default (port 5000)
python -m src.web.server

# Custom port
python -m src.web.server --port 8080

# Debug mode
python -m src.web.server --debug
```

### Dashboard Pages

**Main Dashboard** (`/`):
- Session statistics (total sessions, practice time)
- Recent sessions list
- Quick action buttons

**Real-time** (`/realtime`):
- Live neurofeedback display
- Real-time charts (band powers, meditation depth)
- Current state indicator with color coding
- Power bars for each band
- Session statistics

**History** (`/history`):
- All recorded sessions
- Click to view detailed analysis
- Session comparison tools

### Real-time Page Features

1. **State Display**
   - Large color-coded state indicator
   - Current feedback message
   - Smooth state transitions

2. **Live Charts**
   - Band powers over time (alpha, beta, theta, delta)
   - Meditation depth progression
   - Auto-scrolling time axis

3. **Power Meters**
   - Real-time bars for each frequency band
   - Numerical values updated live
   - Color-coded (alpha=purple, beta=red, theta=blue, delta=green)

4. **Session Stats**
   - Alpha success count
   - Beta success count
   - Perfect state count
   - Session duration timer

---

## Training Tips

### For Beginners

**Week 1-2: Learn the States**
- Start with 5-minute sessions
- Focus on recognizing alpha+ state
- Notice what helps you relax (breathing, body scan)
- Don't worry about beta yet

**Week 3-4: Consistency**
- Increase to 10-minute sessions
- Daily practice (even 5 minutes helps)
- Track your alpha success rate
- Aim for >50% alpha+ states

**Month 2+: Mastery**
- Aim for combined (a+b+) states
- 15-20 minute sessions
- Track learning curve across weeks
- Experiment with different techniques

### Techniques to Try

**To Increase Alpha** (relaxation):
1. **Deep breathing** - Slow, diaphragmatic breaths
2. **Body scan** - Progressive muscle relaxation
3. **Mantra** - Repeat a simple word/phrase
4. **Visualization** - Peaceful scene (beach, forest)

**To Decrease Beta** (mental calm):
1. **Let thoughts pass** - Don't engage with thinking
2. **Simple anchor** - Focus on breath, not analysis
3. **Accept wandering** - Gently return without judgment
4. **Body awareness** - Feel sensations, not thoughts

**To Avoid Drowsiness**:
1. **Posture** - Sit upright, spine straight
2. **Eyes** - Keep slightly open (soft downward gaze)
3. **Timing** - Meditate when alert (morning/afternoon)
4. **Environment** - Cool, well-ventilated room

### Using the Feedback

**Good Practice**:
- ✅ Use feedback as a guide, not a grade
- ✅ Celebrate successes (alpha+, a+b+)
- ✅ Learn from failures (what caused alpha-?)
- ✅ Stay relaxed about the process itself

**Avoid**:
- ❌ Stressing about achieving states
- ❌ Forcing relaxation (creates tension)
- ❌ Judging yourself for "bad" sessions
- ❌ Checking feedback constantly (trust the process)

---

## Troubleshooting

### "Feedback keeps jumping between states"

**Problem**: Too sensitive, states change rapidly

**Solutions**:
```bash
# Increase smoothing window
python scripts/realtime_feedback.py --smoothing 5

# Increase processing window
python scripts/realtime_feedback.py --window-size 3.0
```

### "I'm always in alpha- state"

**Problem**: Baseline thresholds may be too high

**Solutions**:
1. Record a proper baseline (5 min, eyes open, relaxed)
2. Check if you're tense - try deep breathing first
3. Lower thresholds manually (future feature)

### "Audio is too quiet/loud"

```bash
# Quieter
python scripts/realtime_feedback.py --volume 0.3

# Louder
python scripts/realtime_feedback.py --volume 0.8

# No audio
python scripts/realtime_feedback.py --no-audio
```

### "Web dashboard won't connect"

**Check**:
1. Server is running: `python -m src.web.server`
2. Port is correct: `http://localhost:5000/realtime`
3. Firewall allows port 5000
4. Browser console for errors (F12)

### "Muse headband not connecting"

Currently, Muse integration uses mock data. Real Muse support coming soon!

For testing, always use:
```bash
python scripts/realtime_feedback.py --device mock
```

---

## Scientific Background

### Research Basis

Based on **Kovacevic et al. (2015)** "My Virtual Dream" neurofeedback study:

- **523 participants** tested
- **~1 minute** learning speed for brain state modulation
- **Alpha (8-12 Hz)** = reliable relaxation marker
- **Beta (18-30 Hz)** = mental activity marker
- **Personal thresholds** = 0.9× (lower) to 1.1-1.2× (upper) of mean
- **Performance ratio** = (success states) / (failure states)

### Why Real-time Feedback Works

**Operant Conditioning**:
- Brain receives immediate reward (pleasant tone)
- Learns to repeat successful states
- Works unconsciously (don't need to "know how")

**Fast Learning**:
- Brain adapts to feedback in ~1 minute
- Significant improvement in 3-5 sessions
- Sustained with regular practice

**Neuroplasticity**:
- Forms new neural pathways
- Strengthens relaxation response
- Transfers to non-feedback meditation

---

## Advanced Features

### Recording Baseline

Create personalized thresholds (future feature):

```bash
# Record 10-minute baseline (eyes open, relaxed)
python scripts/record_baseline.py --duration 600 --output data/baselines/my_baseline.pkl

# Use in session
python scripts/realtime_feedback.py --baseline data/baselines/my_baseline.pkl
```

### Session Analysis

After recording a session, analyze it:

```bash
python scripts/analyze_meditation.py data/sessions/rt_session_001.pkl
```

### Multi-session Tracking

View learning curve across sessions:

```bash
python scripts/track_learning.py --sessions data/sessions/rt_session_*.pkl
```

### Custom Thresholds

Edit thresholds in code (future: config file):

```python
# In src/realtime/neurofeedback.py
self.thresholds = {
    'alpha_low': 0.12,   # Easier to achieve
    'alpha_high': 0.30,  # Higher standard
    # ...
}
```

---

## Next Steps

1. **Start simple**: 5-minute sessions with mock data
2. **Find your technique**: Try different meditation styles
3. **Track progress**: Save sessions and review
4. **Build routine**: Daily practice, even 5 minutes
5. **Explore web dashboard**: Visual feedback is powerful
6. **Share experiences**: Document what works for you

**Remember**: This is a tool for exploration, not perfection. The journey of learning your own mind is more valuable than any metric.

🧘 **Happy meditating!**
