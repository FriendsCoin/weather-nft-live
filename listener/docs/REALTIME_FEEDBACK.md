# Real-Time Neurofeedback - THE LISTENER

Complete guide to real-time EEG processing and visual feedback for live meditation sessions, museum exhibitions, and performances.

---

## Overview

The real-time neurofeedback system processes live EEG data from Muse S and provides instant visual feedback on meditation state. Perfect for:

- **Live performance** (Aug 2026 exhibition)
- **Personal practice** (see your meditation depth in real-time)
- **Museum installations** (interactive meditation experience)
- **Research** (immediate feedback on brain states)

### Features

✨ **Real-time processing** - 5-second rolling window, updates every 0.5s
🎨 **Visual feedback** - Circle size, color, particles respond to meditation state
📊 **Multiple metrics** - Depth, quality, alpha performance, beta activity
🌐 **WebSocket streaming** - Connect any visualization client
🎯 **Personal calibration** - Adapts to your unique brain patterns
💬 **State messages** - Friendly feedback ("Deep relaxation", "Active mind")

---

## Quick Start

### 1. Setup Muse S Connection

```bash
# Install muselsl (if not already)
pip install muselsl

# Pair Muse S via Bluetooth
# Then start LSL stream
muselsl stream
```

### 2. Start Neurofeedback Server

```bash
# Basic usage
python scripts/live_neurofeedback.py

# With calibration from previous session
python scripts/live_neurofeedback.py --calibrate data/sessions/session_001.h5

# Custom window and update rate
python scripts/live_neurofeedback.py --window 10.0 --update-rate 1.0
```

### 3. Open Visualization

```bash
# Generate test HTML client
python scripts/live_neurofeedback.py --save-client

# Open test_client.html in browser
# You should see live visualization!
```

---

## Architecture

```
┌─────────────┐
│   Muse S    │  EEG headband
│  (4 channels)│
└──────┬──────┘
       │ Bluetooth
       ▼
┌─────────────┐
│   muselsl   │  LSL streaming
│  (pylsl)    │
└──────┬──────┘
       │ LSL stream
       ▼
┌─────────────────────────────────┐
│  RealtimeFeedback               │
│  - Rolling window buffer        │
│  - Feature extraction           │
│  - Meditation metrics           │
│  - Personal thresholds          │
└──────┬──────────────────────────┘
       │ State updates
       ▼
┌─────────────────────────────────┐
│  WebSocket Server               │
│  - Broadcasts state to clients  │
│  - JSON messages                │
└──────┬──────────────────────────┘
       │ ws://localhost:8765
       ▼
┌─────────────────────────────────┐
│  Visualization Clients          │
│  - Web browser (HTML/JS)        │
│  - TouchDesigner (OSC)          │
│  - Processing, p5.js, etc.      │
└─────────────────────────────────┘
```

---

## Meditation Metrics

### Depth (0-100)

**What it measures:** Overall meditation depth

**Formula:**
```
depth = 40% * alpha_power + 30% * theta_power + 30% * (1 - beta_power)
```

**Interpretation:**
- `0-30`: Settling in, active mind
- `30-50`: Light meditation
- `50-70`: Moderate depth
- `70-85`: Deep meditation
- `85-100`: Very deep states

**Visual mapping:** Circle size (larger = deeper)

### Quality (0-100)

**What it measures:** Overall session quality

**Formula:**
```
quality = 40% * alpha_performance + 30% * beta_performance + 30% * depth
```

**Interpretation:**
- `0-40`: Challenging session
- `40-60`: Moderate quality
- `60-80`: Good session
- `80-100`: Excellent session

**Visual mapping:** Brightness/glow intensity

### Alpha Performance

**What it measures:** Relaxation vs. tension

**Values:**
- `+2.0`: Excellent relaxation (alpha+)
- `+1.0`: Good relaxation
- `0.0`: Neutral
- `-1.0`: Some tension
- `-2.0`: High tension (alpha-)

**Visual mapping:** Color hue
- Blue: Deep relaxation
- Cyan/Green: Balanced
- Yellow: Active mind

### Beta Performance

**What it measures:** Mental activity (inverse - lower is better)

**Values:**
- `+1.0`: Calm mind (beta-)
- `0.5`: Moderate
- `-1.0`: Active thinking (beta+)

### State Messages

Real-time feedback messages:

| State | Depth | Alpha | Message |
|-------|-------|-------|---------|
| 🌟 Deep relaxation | >30 | alpha+ | Excellent meditation |
| ✨ Calm and focused | >30 | beta- | Good session |
| 😌 Meditating | >30 | neutral | Maintaining practice |
| 🤔 Active mind | <30 | beta+ | Mind is busy |
| 🌱 Settling in | <30 | neutral | Beginning session |

---

## Calibration

For personalized thresholds, calibrate with a baseline session:

```bash
# Record baseline session (20+ minutes recommended)
python scripts/record_session.py --duration 30 --session-name baseline

# Process it
python scripts/process_session.py --session baseline

# Use for calibration
python scripts/live_neurofeedback.py --calibrate data/sessions/baseline.h5
```

**Calibration computes:**
- Personal alpha thresholds (25th-75th percentile)
- Personal beta thresholds
- Baseline for performance ratios

**Without calibration:** Uses population averages (works fine for most people)

---

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
    console.log('Connected to neurofeedback server');
};

ws.onmessage = (event) => {
    const state = JSON.parse(event.data);
    updateVisualization(state);
};
```

### State Message Format

```json
{
  "timestamp": "2025-11-18T14:30:45.123456",
  "depth": 65.3,
  "depth_smooth": 63.1,
  "quality": 72.5,
  "alpha_power": 0.45,
  "beta_power": 0.22,
  "theta_power": 0.35,
  "alpha_rel": 0.31,
  "beta_rel": 0.15,
  "theta_rel": 0.24,
  "alpha_beta_ratio": 2.04,
  "alpha_state": "alpha+",
  "beta_state": "beta-",
  "alpha_performance": 1.25,
  "beta_performance": 0.75,
  "state_message": "🌟 Deep relaxation",
  "state_level": 4
}
```

### Commands (Client → Server)

```javascript
// Ping
ws.send(JSON.stringify({command: 'ping'}));
// Response: {response: 'pong'}

// Get current state
ws.send(JSON.stringify({command: 'get_state'}));
// Response: <full state object>
```

---

## Visual Feedback Helpers

### Circle Size

Maps depth to circle radius:

```python
from pipeline.realtime_feedback import VisualFeedback

size = VisualFeedback.circle_size(depth, min_size=50, max_size=500)
# depth=0 → 50px
# depth=50 → 275px
# depth=100 → 500px
```

### Color Hue

Maps alpha performance to color:

```python
hue = VisualFeedback.color_hue(alpha_performance)
# alpha=-2 → 240° (blue, calm)
# alpha=0 → 180° (cyan/green, balanced)
# alpha=+2 → 60° (yellow, active)
```

### Particle Density

Maps quality to particle count:

```python
particles = VisualFeedback.particle_density(quality, max_particles=100)
# quality=0 → 0 particles
# quality=50 → 50 particles
# quality=100 → 100 particles
```

### Complete Visual Params

```python
params = VisualFeedback.get_visual_params(state)
# Returns: {
#   'circle_size': 350,
#   'color_hue': 200,
#   'particle_count': 70,
#   'glow_intensity': 0.75,
#   'depth_percent': 70.0,
#   'quality_percent': 70.0,
#   'state_message': "✨ Calm and focused"
# }
```

---

## Advanced Usage

### TouchDesigner Integration

Use OSC instead of WebSocket:

```python
# Install python-osc
pip install python-osc

# Create OSC sender in Python
from pythonosc import udp_client
client = udp_client.SimpleUDPClient("127.0.0.1", 7000)

# In feedback callback
def send_osc(state):
    client.send_message("/depth", state['depth_smooth'])
    client.send_message("/alpha", state['alpha_performance'])
    client.send_message("/quality", state['quality'])
```

In TouchDesigner:
- Add OSC In CHOP
- Port 7000
- Bind to `/depth`, `/alpha`, `/quality`
- Map to visual parameters

### Processing / p5.js

```javascript
// p5.js example
let ws;
let depth = 0;
let alpha = 0;

function setup() {
  createCanvas(800, 600);
  ws = new WebSocket('ws://localhost:8765');
  ws.onmessage = (event) => {
    const state = JSON.parse(event.data);
    depth = state.depth_smooth;
    alpha = state.alpha_performance;
  };
}

function draw() {
  background(0);

  // Map depth to circle size
  let size = map(depth, 0, 100, 50, 500);

  // Map alpha to color
  let hue = map(alpha, -2, 2, 240, 60);
  colorMode(HSB);
  fill(hue, 80, 70);

  // Draw circle
  ellipse(width/2, height/2, size, size);
}
```

### Unity / Unreal Engine

Use WebSocket client libraries:
- Unity: [WebSocket-Sharp](https://github.com/sta/websocket-sharp)
- Unreal: Built-in WebSocket support

---

## Exhibition Setup

### Hardware

**Required:**
- Muse S EEG headband
- Laptop/computer (runs Python backend)
- Display/projector (shows visualization)

**Optional:**
- Speakers (for audio feedback)
- VR headset (immersive experience)

### Software Stack

1. **Backend** (runs on laptop)
   ```bash
   # Terminal 1: LSL stream
   muselsl stream

   # Terminal 2: Neurofeedback
   python scripts/live_neurofeedback.py --calibrate baseline.h5
   ```

2. **Frontend** (runs in browser/app)
   - Web browser: `test_client.html`
   - TouchDesigner: Custom project
   - Processing: Custom sketch

### Network Setup

**Local (single computer):**
- Backend: `localhost:8765`
- Frontend: Connect to `ws://localhost:8765`

**Networked (museum installation):**
```bash
# Backend (computer with Muse S)
python scripts/live_neurofeedback.py --host 0.0.0.0 --port 8765

# Frontend (display computer)
# Connect to ws://[backend-ip]:8765
```

---

## Troubleshooting

### "No EEG stream found"

**Problem:** Can't find Muse S stream

**Solutions:**
1. Check Muse S is paired via Bluetooth
2. Run `muselsl stream` in separate terminal
3. Check stream with `muselsl list`
4. Try restarting Bluetooth/Muse S

### "Connection refused" (WebSocket)

**Problem:** Browser can't connect to server

**Solutions:**
1. Check server is running: `python scripts/live_neurofeedback.py`
2. Check port is correct (default: 8765)
3. Check firewall settings
4. Try `localhost` vs `127.0.0.1`

### Jittery/Unstable Visualization

**Problem:** Visuals jump around too much

**Solutions:**
1. Increase window size: `--window 10.0` (more smoothing)
2. Decrease update rate: `--update-rate 1.0` (slower updates)
3. Check EEG connection quality
4. Reduce muscle artifacts (relax face/jaw)

### Low Depth Scores

**Problem:** Depth stays near 0 even during meditation

**Solutions:**
1. Calibrate with personal baseline: `--calibrate baseline.h5`
2. Check electrode contact (wet hair if needed)
3. Give it time (brain needs 5+ min to settle)
4. Thresholds may need adjustment

---

## Performance

**Latency:**
- EEG sampling: 256 Hz (~4ms per sample)
- Processing: ~50-100ms (rolling window)
- WebSocket: <10ms
- **Total: ~100-150ms** (acceptable for real-time)

**CPU Usage:**
- Idle: ~5% (one core)
- Processing: ~15-25%
- With visualization: +10-20%

**Memory:**
- Backend: ~200-300 MB
- 5-second buffer: ~5 KB
- Negligible RAM usage

---

## Future Enhancements

### Planned Features

- [ ] OSC server (for TouchDesigner)
- [ ] Recording capability (save live sessions)
- [ ] Multi-session comparison (live vs. best)
- [ ] Audio feedback (binaural beats matching brain state)
- [ ] Mobile app (iOS/Android viewer)
- [ ] VR integration (Quest, Vive)

### Community Contributions

Want to create custom visualizations?

1. Connect to WebSocket (`ws://localhost:8765`)
2. Parse JSON state messages
3. Map metrics to your visuals
4. Share your creation!

---

## Examples

### Minimal Visualization (HTML)

```html
<!DOCTYPE html>
<html>
<body>
    <h1 id="message">Connecting...</h1>
    <div id="circle" style="width:100px; height:100px;
                             border-radius:50%; background:blue;"></div>
    <script>
        const ws = new WebSocket('ws://localhost:8765');
        ws.onmessage = (e) => {
            const s = JSON.parse(e.data);
            document.getElementById('message').textContent = s.state_message;
            const circle = document.getElementById('circle');
            circle.style.width = (50 + s.depth_smooth * 4) + 'px';
            circle.style.height = (50 + s.depth_smooth * 4) + 'px';
        };
    </script>
</body>
</html>
```

### Python Visualization (matplotlib)

```python
import asyncio
import websockets
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

depth_history = []

async def receive():
    async with websockets.connect('ws://localhost:8765') as ws:
        async for message in ws:
            state = json.loads(message)
            depth_history.append(state['depth_smooth'])
            if len(depth_history) > 100:
                depth_history.pop(0)

# Run in background thread
import threading
threading.Thread(target=lambda: asyncio.run(receive()), daemon=True).start()

# Animate plot
fig, ax = plt.subplots()
def update(frame):
    ax.clear()
    ax.plot(depth_history)
    ax.set_ylim(0, 100)
    ax.set_title('Real-time Meditation Depth')

ani = FuncAnimation(fig, update, interval=100)
plt.show()
```

---

## References

- [MNE-Python](https://mne.tools/) - EEG processing
- [WebSockets](https://websockets.readthedocs.io/) - Real-time communication
- [Muse LSL](https://github.com/alexandrebarachant/muse-lsl) - Muse S streaming
- [TouchDesigner](https://derivative.ca/) - Visual programming

---

## Summary

**Real-time neurofeedback is ready!** 🎉

Start your first live session:

```bash
# 1. Stream Muse S
muselsl stream

# 2. Start neurofeedback (new terminal)
python scripts/live_neurofeedback.py

# 3. Open visualization (browser)
open test_client.html
```

**Next steps:**
- Create custom visualizations
- Integrate with TouchDesigner
- Prepare for exhibition (Aug 2026)

---

**Last updated:** November 18, 2025
