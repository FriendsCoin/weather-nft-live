```markdown
# NESCIENCE Visualization Options

Multiple ways to visualize meditation states - from simple (native Python) to complex (TouchDesigner).

## Overview

| Option | Complexity | Requirements | Best For |
|--------|------------|--------------|----------|
| **Native Matplotlib** | ⭐ Easy | Just Python | Testing, development, personal use |
| **Terminal Only** | ⭐ Easiest | Just Python | Headless, minimal |
| **Web Dashboard** | ⭐⭐ Medium | Browser | Monitoring, remote access |
| **TouchDesigner** | ⭐⭐⭐ Complex | TD license | Live performance, gallery |

---

## 1. Native Matplotlib Visualization (RECOMMENDED FOR TESTING)

### What It Is
Real-time visualization using Python's matplotlib library.
No external software required!

### Features
- Real-time state display (SETTLING, FLOW, DEEP, etc.)
- Band power history graphs (alpha, beta, theta, delta)
- Current band power meters
- Character awakening progress circle
- State intensity history
- Poetry/description display

### Usage

```bash
# Mock data (testing)
python scripts/nescience_session.py --visualize --mock --duration 600

# Real Muse S
python scripts/nescience_session.py --visualize --duration 1200
```

### Screenshot Description
```
┌─────────────────────────────────────────────────────────┐
│                      FLOW                                │
│  [Large colored rectangle pulsing with intensity]       │
│                  Intensity: 0.73                         │
├─────────────────────────────────────────────────────────┤
│  Band Power History     │  Current Meters               │
│  [Line graphs]          │  Alpha   ████████  0.65      │
│                         │  Beta    ████       0.42      │
│                         │  Theta   ██████     0.58      │
│                         │  Delta   ███        0.35      │
├─────────────────────────────────────────────────────────┤
│  Awakening    │ Intensity  │  Poetry                    │
│    ◐ 15%      │ [Graph]    │  "Natural movement         │
│               │            │   of breath"               │
└─────────────────────────────────────────────────────────┘
```

### Pros & Cons

**Pros:**
- ✓ No external software
- ✓ Easy to set up
- ✓ Real-time feedback
- ✓ Perfect for development
- ✓ Works on any platform

**Cons:**
- ✗ Not suitable for large projections
- ✗ Basic aesthetics (not art-quality)
- ✗ Limited customization

### When to Use
- Testing hardware setup
- Personal practice
- Development
- Debugging state classification
- Simple installations

---

## 2. Terminal Only (MINIMAL)

### What It Is
Text-only output in terminal. No graphics at all.

### Usage

```bash
# Default nescience_session.py
python scripts/nescience_session.py --mock --duration 600
```

### Output Example
```
[SETTLING] intensity:0.65 α:0.42 β:0.38 θ:0.51 | Ripples across a dark pond
[FLOW] intensity:0.73 α:0.58 β:0.25 θ:0.45 | Natural movement of breath
[DEEP] intensity:0.84 α:0.72 β:0.18 θ:0.68 | Profound stillness emerges
```

### Pros & Cons

**Pros:**
- ✓ Simplest option
- ✓ Low resource usage
- ✓ Works over SSH
- ✓ Easy to log

**Cons:**
- ✗ No visual feedback
- ✗ Hard to see patterns
- ✗ Not suitable for performance

### When to Use
- Headless servers
- SSH sessions
- Logging/recording
- Minimal resource usage needed

---

## 3. Web Dashboard

### What It Is
Browser-based interface with real-time WebSocket updates.

### Features
- Character status card
- System status
- Session history
- One-click session launching
- Remote monitoring

### Usage

```bash
# Start dashboard server
python start_dashboard.py

# Open in browser
http://localhost:8080
```

### Screenshot Description
```
┌─────────────────────────────────────────────────────────┐
│                  NESCIENCE Dashboard                     │
├─────────────────────────────────────────────────────────┤
│  Companion State     │  System Status                   │
│  Phase: WITNESSING   │  Baseline: ✓ Calibrated         │
│  Awakening: 15%      │  Last Session: 2h ago           │
│  ████░░░░░░░░        │                                  │
│  Sessions: 12        │                                  │
│                      │                                  │
│  Personality:        │                                  │
│  Curiosity   ██████  │                                  │
│  Stillness   ████    │                                  │
│  Wildness    ███     │                                  │
├─────────────────────────────────────────────────────────┤
│  Actions                                                 │
│  [Start Session] [Calibrate] [Autonomous] [Visualize]  │
├─────────────────────────────────────────────────────────┤
│  Recent Sessions                                         │
│  session_012  2025-01-15  12min  FLOW, DEEP, PRESENT   │
│  session_011  2025-01-14  15min  SETTLING, FLOW         │
└─────────────────────────────────────────────────────────┘
```

### Pros & Cons

**Pros:**
- ✓ Access from any device
- ✓ Clean interface
- ✓ Session history
- ✓ Remote monitoring
- ✓ Mobile-friendly

**Cons:**
- ✗ Not real-time visualization (just status)
- ✗ Requires server running
- ✗ Not suitable for performance

### When to Use
- Monitoring multiple sessions
- Remote access needed
- Non-technical users
- Session management

---

## 4. TouchDesigner (PROFESSIONAL)

### What It Is
Professional real-time graphics software. Industry standard for live visuals.

### Features
- Custom shader-based visuals
- Projection mapping
- Multi-screen setups
- DMX lighting control
- Audio-reactive
- Generative art

### Setup

See: `docs/TOUCHDESIGNER_SETUP.md`

```bash
# Run session with TD integration
python scripts/nescience_session.py --touchdesigner localhost:9000
```

**In TouchDesigner:**
1. Add OSC In DAT (port 9000)
2. Parse `/nescience/*` messages
3. Create reactive visuals

### OSC Messages Sent

```
/nescience/state <string>         # SETTLING, FLOW, etc.
/nescience/intensity <float>      # 0-1
/nescience/bands <4 floats>       # alpha, beta, theta, delta
/nescience/awakening <float>      # 0-1
/nescience/poetry <string>        # Description
```

### Example TD Network

```
OSC In DAT (port 9000)
    ↓
Select DAT (filter /nescience/state)
    ↓
Text TOP (display state)
    ↓
Composite TOP (blend with generative visuals)
    ↓
Feedback TOP (create trails)
    ↓
Projection output
```

### Pros & Cons

**Pros:**
- ✓ Professional quality
- ✓ Infinite customization
- ✓ Multi-screen support
- ✓ Industry standard
- ✓ Gallery-ready

**Cons:**
- ✗ Steep learning curve
- ✗ License required ($600 Pro)
- ✗ GPU-intensive
- ✗ Complex setup

### When to Use
- Live performances
- Gallery installations
- Professional productions
- Custom visuals needed
- Multi-projector setups

---

## Comparison Table

### Feature Matrix

| Feature | Native | Terminal | Dashboard | TouchDesigner |
|---------|--------|----------|-----------|---------------|
| **Real-time State** | ✓ | ✓ | ✗ | ✓ |
| **Band Powers** | ✓ | ✓ | ✗ | ✓ |
| **History Graphs** | ✓ | ✗ | ✓ | ✓ (custom) |
| **Awakening Progress** | ✓ | ✗ | ✓ | ✓ (custom) |
| **Poetry Display** | ✓ | ✓ | ✗ | ✓ (custom) |
| **Remote Access** | ✗ | ✗ | ✓ | ✗ |
| **Projection** | ✗ | ✗ | ✗ | ✓ |
| **Customization** | Limited | Limited | Limited | Unlimited |
| **Setup Time** | 1 min | 1 min | 2 min | Hours |

### Resource Usage

| Option | CPU | RAM | GPU | Network |
|--------|-----|-----|-----|---------|
| **Native** | Medium | Low | Low | None |
| **Terminal** | Low | Low | None | None |
| **Dashboard** | Low | Low | None | Local |
| **TouchDesigner** | High | High | High | OSC |

---

## Workflows by Use Case

### Development & Testing

**Recommended:** Native Matplotlib

```bash
# Test with visualization
python scripts/nescience_session.py --visualize --mock --duration 300
```

**Why:** Immediate visual feedback, no setup, easy debugging.

---

### Personal Practice

**Options:**

**1. Native (If you like visuals):**
```bash
python scripts/nescience_session.py --visualize --duration 1200
```

**2. Dashboard (If you want history):**
```bash
python start_dashboard.py
# Then use dashboard to launch sessions
```

**3. Terminal (Minimal distraction):**
```bash
python scripts/nescience_session.py --duration 1200
```

---

### Live Performance

**Recommended:** TouchDesigner

**Setup:**
```bash
# Terminal 1: Dashboard (monitoring)
python start_dashboard.py

# Terminal 2: Session with TD
python scripts/nescience_session.py --touchdesigner localhost:9000

# TouchDesigner: Visuals output to projector
```

**Why:** Professional quality, real-time reactivity, projection-ready.

---

### Gallery Installation

**Option 1: Autonomous + TouchDesigner (No human)**

```bash
python scripts/autonomous_meditation.py --touchdesigner localhost:9000
```

**Option 2: Interactive + Native (Visitors participate)**

```bash
# Visitors see real-time matplotlib visualization
python scripts/nescience_session.py --visualize --duration 600
```

---

### Research / Data Collection

**Recommended:** Terminal + Logging

```bash
# Log to file
python scripts/nescience_session.py --duration 1200 2>&1 | tee session_log.txt
```

**Why:** Minimal overhead, easy to parse logs, focus on data not visuals.

---

## Combining Multiple Visualizations

### Can You Run Multiple?

**Yes!** You can run different visualizations simultaneously:

**Example: Development Setup**

```bash
# Terminal 1: Dashboard (monitoring)
python start_dashboard.py

# Terminal 2: Session with native visualization
python scripts/nescience_session.py --visualize --mock --duration 600

# Both show same session!
```

**Example: Performance Setup**

```bash
# Terminal 1: Dashboard (technician view)
python start_dashboard.py

# Terminal 2: Session with TouchDesigner (audience view)
python scripts/nescience_session.py --touchdesigner localhost:9000

# Technician monitors dashboard while audience sees TD visuals
```

---

## Quick Reference

### Start Native Visualization
```bash
python scripts/nescience_session.py --visualize --mock --duration 600
```

### Start Dashboard
```bash
python start_dashboard.py
# → http://localhost:8080
```

### Start with TouchDesigner
```bash
python scripts/nescience_session.py --touchdesigner localhost:9000
```

### Start Terminal Only
```bash
python scripts/nescience_session.py --mock --duration 600
```

---

## Troubleshooting

### Native Visualization: "Display backend error"

**Mac:** Install Python with proper Tk support
```bash
brew install python-tk
```

**Linux:** Install matplotlib backend
```bash
sudo apt-get install python3-tk
```

**WSL/Headless:** Native won't work, use Terminal or Dashboard instead

### TouchDesigner: "No OSC messages received"

Check:
1. TD listening on correct port (9000)
2. Python sending to correct host/port
3. Firewall allows OSC traffic
4. Use `scripts/test_osc.py --send --port 9000` to test

### Dashboard: "Can't connect to server"

Check:
1. Dashboard server running (`python start_dashboard.py`)
2. Correct URL (http://localhost:8080)
3. Port not in use by other app
4. Firewall allows port 8080

---

## Recommendations

**For most users:** Start with **Native Matplotlib** for testing, then move to **TouchDesigner** for performances if needed.

**Simplest path:**
1. Test with Native: `python scripts/nescience_session.py --visualize --mock --duration 300`
2. Verify hardware with Terminal: `python scripts/nescience_session.py --duration 600`
3. Use Dashboard for monitoring: `python start_dashboard.py`
4. Add TouchDesigner only if needed for performance

**Don't over-complicate!** Native visualization is perfectly fine for most use cases.

---

**Next Steps:**

1. Try native visualization: `python scripts/nescience_session.py --visualize --mock --duration 300`
2. If it works, you're ready for real sessions!
3. Add TouchDesigner later only if needed for performance/gallery

**Visualization is optional - meditation is what matters.** 🧘
```
