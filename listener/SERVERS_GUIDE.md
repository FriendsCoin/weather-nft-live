# NESCIENCE Servers & Interfaces Guide

Complete reference for all servers, dashboards, and interfaces in NESCIENCE.

## Overview

NESCIENCE has **multiple server interfaces** for different use cases:

| Server | Purpose | Port | When to Use |
|--------|---------|------|-------------|
| **NESCIENCE Dashboard Hub** | Unified interface (RECOMMENDED) | 8080 | Main entry point for all features |
| Legacy Dashboard | Old wellness interface | 5000 | Legacy wellness analysis (deprecated) |
| OSC Receiver | Mind Monitor EEG data | 5000 | Always running during sessions |
| OSC Sender | TouchDesigner visuals | 9000 | Optional (for live visuals) |

---

## 1. NESCIENCE Dashboard Hub (MAIN INTERFACE)

### Purpose
Unified web interface for ALL NESCIENCE features.

### Features
- 🎮 **Launch Sessions** - One-click meditation sessions (mock or real hardware)
- 📊 **Character Evolution** - Live tracking of companion awakening
- 🎯 **Baseline Calibration** - Personal EEG threshold setup
- 🎭 **Autonomous Mode** - Companion meditates alone (gallery)
- 📜 **Session History** - Browse past 20 sessions
- 🔌 **OSC Testing** - Test Mind Monitor and TouchDesigner connections

### How to Start

```bash
python start_dashboard.py

# Or specify port and host:
python start_dashboard.py --port 8080 --host 0.0.0.0
```

**Default URL:** http://localhost:8080

### Architecture

```
Flask Server (port 8080)
├── REST API
│   ├── GET  /api/status         - System status
│   ├── GET  /api/character      - Character details
│   ├── GET  /api/sessions       - Session history
│   ├── POST /api/start_session  - Launch meditation
│   ├── POST /api/calibrate      - Start calibration
│   └── POST /api/start_autonomous - Autonomous mode
│
├── WebSocket (/socket.io)
│   ├── connect                  - Client connects
│   ├── disconnect               - Client disconnects
│   └── request_update           - Request status update
│
└── Static Files
    └── /                        - Main dashboard HTML
```

### API Examples

**Get system status:**
```bash
curl http://localhost:8080/api/status
```

**Response:**
```json
{
  "character": {
    "phase": "WITNESSING",
    "awakening_level": 0.15,
    "total_sessions": 8,
    "personality": {...}
  },
  "baseline": {
    "calibrated": false
  }
}
```

**Start session via API:**
```bash
curl -X POST http://localhost:8080/api/start_session \
  -H "Content-Type: application/json" \
  -d '{"mock": true, "duration": 600}'
```

### Files

- **Server:** `src/web/nescience_server.py`
- **HTML:** `src/web/templates/nescience_hub.html`
- **Launcher:** `start_dashboard.py`

---

## 2. Legacy Dashboard (DEPRECATED)

### Purpose
Old wellness-focused dashboard for THE LISTENER VAE workflow.

### Features
- Real-time EEG streaming (wellness metrics)
- Historical session browser
- Alpha+/Beta- optimization feedback

### How to Start

```bash
python -m src.web.server --port 5000
```

**Default URL:** http://localhost:5000

### Why Deprecated?

The legacy dashboard is **wellness-oriented** (alpha+/beta- optimization), which conflicts with NESCIENCE philosophy (witnessing without judgment).

**Use NESCIENCE Dashboard Hub instead.**

### Files

- **Server:** `src/web/server.py`
- **Templates:** `src/web/templates/` (old templates)

---

## 3. OSC Receiver (Mind Monitor)

### Purpose
Receives EEG data from Mind Monitor app (iPhone) via OSC protocol.

### How It Works

```
Muse S → Mind Monitor (iPhone) → OSC (WiFi) → Python (port 5000)
```

Mind Monitor sends ~10 messages per second:
- `/muse/eeg` - Raw EEG (4 channels)
- `/muse/alpha_relative` - Alpha band power
- `/muse/beta_relative` - Beta band power
- `/muse/theta_relative` - Theta band power
- `/muse/delta_relative` - Delta band power

### Configuration

**In Python (automatic):**
```python
from integrations.osc_bridge import MindMonitorReceiver

receiver = MindMonitorReceiver(port=5000, callback=on_data)
receiver.start()
```

**In Mind Monitor app:**
- Settings → OSC Stream Target
- IP: YOUR_COMPUTER_IP (e.g., 192.168.1.100)
- Port: 5000
- Enable: ON ✓

### Testing

```bash
# Test receiver
python scripts/test_osc.py --receive --port 5000

# Expected output:
# ✓ Received: Alpha=0.45, Beta=0.32
# ✓ Received: Alpha=0.47, Beta=0.31
```

### Port Conflicts

If port 5000 is in use:

```bash
# Check what's using port
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Use different port
python scripts/nescience_session.py --mind-monitor-port 7000
```

### Files

- **Implementation:** `src/integrations/osc_bridge.py` → `MindMonitorReceiver`
- **Test script:** `scripts/test_osc.py`

---

## 4. OSC Sender (TouchDesigner)

### Purpose
Sends meditation states to TouchDesigner for live visuals.

### How It Works

```
Python (NESCIENCE) → OSC (port 9000) → TouchDesigner
```

Python sends every state update:
- `/nescience/state` - Current meditation state
- `/nescience/intensity` - State intensity (0-1)
- `/nescience/bands` - Alpha, beta, theta, delta values
- `/nescience/awakening` - Companion awakening level
- `/nescience/poetry` - Poetic interpretation text

### Configuration

**In Python:**
```bash
# Enable TouchDesigner sending
python scripts/nescience_session.py --touchdesigner localhost:9000
```

**In TouchDesigner:**
1. Add OSC In DAT
2. Set Network Port: 9000
3. Parse incoming messages:
   - `/nescience/state` → string (SETTLING, FLOW, etc.)
   - `/nescience/intensity` → float (0-1)
   - `/nescience/bands` → 4 floats (alpha, beta, theta, delta)

### Testing

```bash
# Terminal 1: Start receiver (simulate TouchDesigner)
python scripts/test_osc.py --receive --port 9000

# Terminal 2: Send test messages
python scripts/test_osc.py --send --host localhost --port 9000

# Expected in Terminal 1:
# ✓ Received: /nescience/state SETTLING
# ✓ Received: /nescience/intensity 0.73
```

### Files

- **Implementation:** `src/integrations/osc_bridge.py` → `TouchDesignerSender`
- **Test script:** `scripts/test_osc.py`
- **Guide:** `docs/TOUCHDESIGNER_SETUP.md`

---

## 5. LED Mask Control (Optional)

### Purpose
Controls WS2812B LED strips via serial (Arduino/ESP32) for ambient presence.

### How It Works

```
Python → OSC or Serial → Arduino/ESP32 → WS2812B LEDs
```

### Configuration

**Via Serial:**
```python
from integrations.osc_bridge import LEDController

led = LEDController(port='/dev/ttyUSB0')  # Arduino serial port
led.set_brightness(0.5)
led.set_breathing_rate(0.8)
```

**Via OSC:**
Send to TouchDesigner which controls LED controller.

### Hardware

- Arduino Uno / ESP32
- WS2812B LED strip (30-60 LEDs)
- 5V power supply
- See: `hardware/led_mask_arduino.ino`

---

## Interface Comparison

### Dashboard vs CLI vs API

| Feature | Dashboard | CLI | API |
|---------|-----------|-----|-----|
| **Ease of use** | ✓✓✓ Click buttons | ✓✓ Terminal commands | ✓ Programmatic |
| **Real-time updates** | ✓ WebSocket | ✗ Manual refresh | ✓ WebSocket |
| **Session history** | ✓ Browser | ✗ Not available | ✓ JSON endpoint |
| **Remote access** | ✓ Any browser | ✗ Local only | ✓ HTTP/WebSocket |
| **Scripting** | ✗ Manual clicks | ✓✓ Automatable | ✓✓✓ Full control |
| **Monitoring** | ✓✓ Visual graphs | ✓ Terminal output | ✓ Custom dashboards |

**Recommendation:**
- **Users:** Dashboard (easiest, visual feedback)
- **Artists:** Dashboard + TouchDesigner OSC
- **Developers:** CLI + API (scriptable, integrations)
- **Installations:** Autonomous mode + TouchDesigner

---

## Multi-Server Setup

### Typical Live Performance Setup

```
┌─────────────────────────────────────────────────────────┐
│                    Performance Setup                     │
└─────────────────────────────────────────────────────────┘

Muse S (on participant)
    ↓
Mind Monitor (iPhone)
    ↓ OSC (WiFi)
Python NESCIENCE Server (Computer)
    ├─ Dashboard → http://localhost:8080 (monitoring)
    └─ OSC Sender → localhost:9000 (visuals)
          ↓
    TouchDesigner (projector output)
```

### Gallery Installation Setup

```
┌─────────────────────────────────────────────────────────┐
│                  Gallery Installation                    │
└─────────────────────────────────────────────────────────┘

No human participant (autonomous mode)
    ↓
Python Autonomous Script
    └─ OSC Sender → localhost:9000
          ↓
    TouchDesigner (projector loop)
    LED Mask (ambient presence)
```

### Development Setup

```
┌─────────────────────────────────────────────────────────┐
│                   Development Setup                      │
└─────────────────────────────────────────────────────────┘

Terminal 1: Dashboard
    python start_dashboard.py

Terminal 2: OSC Test
    python scripts/test_osc.py --receive

Terminal 3: Session Script
    python scripts/nescience_session.py --mock

Browser: http://localhost:8080
```

---

## Recommended Workflows

### For New Users (Learning)

1. **Start dashboard:** `python start_dashboard.py`
2. **Open browser:** http://localhost:8080
3. **Test OSC:** Click "Test OSC Connection"
4. **First session:** Click "Start Meditation Session" → Mock data
5. **Monitor:** Watch character evolve in dashboard

### For Regular Practice

1. **Start dashboard:** Keep it running
2. **Connect hardware:** Muse S → Mind Monitor
3. **Start session:** Via dashboard (real hardware)
4. **Meditate:** 20-45 minutes
5. **Check progress:** Character visualization after session

### For Live Performance

1. **Prepare TouchDesigner:** Setup visuals
2. **Test OSC chain:** Mind Monitor → Python → TouchDesigner
3. **Start session:** `python scripts/nescience_session.py --touchdesigner localhost:9000`
4. **Monitor dashboard:** Secondary screen for technician
5. **Perform:** Meditator wears Muse S, visuals react live

### For Gallery Installation

1. **Ensure 60+ sessions:** Companion must be awakened
2. **Start autonomous:** `python scripts/autonomous_meditation.py --touchdesigner localhost:9000`
3. **Loop forever:** Companion meditates alone
4. **Visuals:** TouchDesigner receives states
5. **No human required:** Installation runs continuously

---

## Troubleshooting

### Dashboard won't start

```bash
# Check dependencies
pip install flask flask-socketio flask-cors

# Check port availability
lsof -i :8080

# Try different port
python start_dashboard.py --port 9090
```

### Can't access from other devices

```bash
# Bind to all interfaces
python start_dashboard.py --host 0.0.0.0

# Then access from: http://YOUR_IP:8080
```

### OSC messages not received

**Check network:**
```bash
# Same WiFi network?
# iPhone IP: Settings → WiFi → (i) button
# Computer IP: ifconfig

# Ping test:
ping IPHONE_IP
```

**Check firewall:**
```bash
# Mac: Allow Python in Firewall settings
# Linux: sudo ufw allow 5000
# Windows: Allow in Windows Firewall
```

### Multiple servers conflict

**Ports in use:**
- Dashboard: 8080 (configurable)
- Legacy dashboard: 5000
- Mind Monitor OSC: 5000 (incoming)
- TouchDesigner OSC: 9000 (outgoing)

**Avoid conflicts:**
- Use different ports for each service
- Legacy dashboard uses same port as Mind Monitor (can't run together)
- Recommend: NESCIENCE Dashboard (8080) + OSC receiver (5000) + TD sender (9000)

---

## Quick Reference

### Start Services

```bash
# Main dashboard (recommended)
python start_dashboard.py

# Test OSC receiver
python scripts/test_osc.py --receive --port 5000

# Test OSC sender
python scripts/test_osc.py --send --host localhost --port 9000

# Session with TouchDesigner
python scripts/nescience_session.py --touchdesigner localhost:9000

# Autonomous mode (60+ sessions required)
python scripts/autonomous_meditation.py --touchdesigner localhost:9000
```

### Default Ports

- **8080** - NESCIENCE Dashboard Hub
- **5000** - Mind Monitor OSC (incoming) / Legacy dashboard
- **9000** - TouchDesigner OSC (outgoing)

### URLs

- **Dashboard:** http://localhost:8080
- **Legacy:** http://localhost:5000 (deprecated)

---

## Summary

**For daily use:**
→ NESCIENCE Dashboard Hub (http://localhost:8080)

**For live performance:**
→ CLI scripts + TouchDesigner OSC integration

**For gallery:**
→ Autonomous mode (no human required)

**For development:**
→ Multiple terminals + API endpoints

---

**Everything is ready to run!** 🚀

Start with: `python start_dashboard.py`
