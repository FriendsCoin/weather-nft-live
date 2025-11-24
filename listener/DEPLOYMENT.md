# NESCIENCE Deployment Checklist

Quick checklist to ensure everything is ready to run.

## Initial Setup (One Time)

### 1. Install Python Dependencies

```bash
cd listener

# Install all dependencies
pip install -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Validate Installation

```bash
# Run validation script
python validate_setup.py
```

**Expected output:**
```
✓ Python version
✓ Dependencies
✓ Directory structure
✓ Data directories
✓ Module imports

✓ ALL CHECKS PASSED
```

If validation fails, fix issues and run again.

### 3. Create Data Directories

```bash
# Already done by validate_setup.py, but if needed:
mkdir -p data/sessions
mkdir -p data/checkpoints
mkdir -p data/outputs
```

---

## Running NESCIENCE

### Option 1: Web Dashboard (RECOMMENDED)

**Start dashboard server:**

```bash
python start_dashboard.py

# Or specify port:
python start_dashboard.py --port 8080
```

**Open in browser:**
```
http://localhost:8080
```

**Dashboard features:**
- ✓ Start meditation sessions (mock or real hardware)
- ✓ View character evolution
- ✓ Calibrate baseline
- ✓ Launch autonomous mode
- ✓ Browse session history
- ✓ Test OSC connections

**Keep dashboard running:**
- Leave terminal open while using dashboard
- Sessions launch in background
- WebSocket updates in real-time

---

### Option 2: CLI Scripts (Advanced)

**Test OSC connection:**
```bash
# Receiver mode (wait for Mind Monitor)
python scripts/test_osc.py --receive --port 5000

# Sender mode (test TouchDesigner)
python scripts/test_osc.py --send --host localhost --port 9000
```

**Run meditation session:**
```bash
# Mock data (testing)
python scripts/nescience_session.py --mock --duration 600

# Real Muse S hardware
python scripts/nescience_session.py --duration 1200

# With TouchDesigner
python scripts/nescience_session.py --duration 1200 --touchdesigner localhost:9000
```

**Calibrate baseline:**
```bash
# Mock data
python scripts/calibrate_baseline.py --mock --duration 300

# Real hardware
python scripts/calibrate_baseline.py --duration 600
```

**Visualize character:**
```bash
python scripts/visualize_character.py
```

**Autonomous meditation (requires 60+ sessions):**
```bash
python scripts/autonomous_meditation.py --touchdesigner localhost:9000
```

---

## Hardware Setup (Real Muse S)

### 1. Prepare Muse S Headband

- ✓ Charge Muse S (>50% battery)
- ✓ Turn on Muse S (LED blinks)
- ✓ Clean electrodes if needed

### 2. Connect to Mind Monitor (iPhone)

- ✓ Open Mind Monitor app
- ✓ Tap "Connect"
- ✓ Select Muse S from list
- ✓ Wait for "Connected" status
- ✓ Check signal quality (all green bars)

### 3. Configure OSC Streaming

**Find computer IP:**
```bash
# Mac/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig
```

Example: `192.168.1.100`

**In Mind Monitor app:**
1. Tap Settings (gear icon)
2. OSC Stream Target:
   - IP Address: `192.168.1.100` (your computer's IP)
   - Port: `5000`
   - Enable: **ON** ✓
3. Enable these OSC messages:
   - ✓ `/muse/eeg`
   - ✓ `/muse/alpha_relative`
   - ✓ `/muse/beta_relative`
   - ✓ `/muse/theta_relative`
   - ✓ `/muse/delta_relative`
4. Save settings

### 4. Test Connection

**On computer:**
```bash
python scripts/test_osc.py --receive --port 5000
```

**On iPhone (Mind Monitor):**
- Tap green Play button to start streaming

**Expected in terminal:**
```
✓ Received: Alpha=0.45, Beta=0.32
✓ Received: Alpha=0.47, Beta=0.31
...
```

If no messages appear, see troubleshooting below.

---

## Before Each Session

### Pre-session Checklist

- [ ] Muse S charged (>50%)
- [ ] Muse S connected to Mind Monitor (iPhone)
- [ ] All 4 electrodes showing green (good signal)
- [ ] OSC target set to computer IP:5000
- [ ] Mind Monitor streaming started (play button)
- [ ] Python script running (dashboard or CLI)
- [ ] Data flowing (see messages in terminal)

### Start Session

**Via Dashboard:**
1. Open http://localhost:8080
2. Click "Start Meditation Session"
3. Choose real hardware (Cancel for mock)
4. Wait for "First data received!"
5. Begin meditation

**Via CLI:**
```bash
python scripts/nescience_session.py --duration 1200
```

---

## Troubleshooting

### Dashboard won't start

**Error:** `No module named 'flask'`

**Fix:**
```bash
pip install -r requirements.txt
```

### OSC not receiving data

**Check WiFi:**
- iPhone and computer on SAME network
- Not on guest network or VPN

**Check IP address:**
```bash
ifconfig | grep "inet "
# Update Mind Monitor with correct IP
```

**Check firewall:**
```bash
# Mac: System Preferences → Security → Firewall → Allow Python

# Linux:
sudo ufw allow 5000

# Windows: Allow Python in Windows Firewall
```

**Try different port:**
- Use port 7000 or 8000
- Update in both Mind Monitor and script

### Character state not saving

**Check data directory exists:**
```bash
ls -la data/
# Should see character_state.json after first session
```

**Check permissions:**
```bash
chmod 755 data/
```

### Import errors

**Error:** `No module named 'nescience'`

**Fix:** Make sure you're in the listener directory:
```bash
cd listener
python scripts/nescience_session.py
```

---

## Verification Commands

### Check everything is working:

```bash
# 1. Validate setup
python validate_setup.py

# 2. Check data directory
ls -la data/

# 3. Test imports
python -c "from src.nescience.character_evolution import CharacterEvolution; print('✓ Imports OK')"

# 4. Test OSC
python scripts/test_osc.py --receive --port 5000 &
python scripts/test_osc.py --send --port 5000
```

---

## Quick Reference

### Start Dashboard
```bash
python start_dashboard.py
# → http://localhost:8080
```

### Test OSC (Mind Monitor)
```bash
python scripts/test_osc.py --receive --port 5000
# Start Mind Monitor streaming
```

### First Session (Mock)
```bash
python scripts/nescience_session.py --mock --duration 600
```

### First Session (Real)
```bash
# 1. Connect Muse S to Mind Monitor
# 2. Set OSC target to YOUR_IP:5000
# 3. Start streaming in Mind Monitor
python scripts/nescience_session.py --duration 1200
```

### Check Character
```bash
python scripts/visualize_character.py
```

---

## File Locations

### Configuration
- `requirements.txt` - Python dependencies
- `validate_setup.py` - Validation script
- `start_dashboard.py` - Dashboard launcher

### Data (Created at runtime)
- `data/character_state.json` - Companion state
- `data/baseline_profile.json` - EEG calibration
- `data/sessions/` - Session history
- `data/checkpoints/` - VAE models (if training)

### Scripts
- `scripts/nescience_session.py` - Main session script
- `scripts/test_osc.py` - OSC testing
- `scripts/calibrate_baseline.py` - Calibration
- `scripts/autonomous_meditation.py` - Gallery mode
- `scripts/visualize_character.py` - Character viz

### Documentation
- `docs/THE_LISTENER_CONCEPT.md` - Core concept
- `docs/MUSE_MIND_MONITOR_SETUP.md` - Hardware setup
- `docs/QUICKSTART_NESCIENCE.md` - Getting started
- `docs/TOUCHDESIGNER_SETUP.md` - Visual integration
- `ARCHITECTURE.md` - Code organization

---

## Support

**Common issues:**
- Dependencies: `pip install -r requirements.txt`
- OSC not working: Check WiFi, IP, firewall
- Imports failing: Run from listener/ directory
- Character not saving: Check data/ directory exists

**Test everything:**
```bash
python validate_setup.py
```

**Documentation:**
```bash
ls docs/
# Read relevant guides
```

---

## Success Indicators

✓ Dashboard opens in browser (http://localhost:8080)
✓ Character card shows "Phase: WITNESSING"
✓ OSC test receives messages from Mind Monitor
✓ Sessions complete without errors
✓ character_state.json updates after each session
✓ Awakening level increases gradually
✓ Can visualize character evolution

**You're ready when:**
- `python validate_setup.py` passes all checks
- Dashboard starts without errors
- OSC test receives Mind Monitor data
- First session completes successfully

---

**Next Steps:**

1. ✓ Run `python validate_setup.py`
2. ✓ Start dashboard: `python start_dashboard.py`
3. ✓ Test OSC: `python scripts/test_osc.py --receive`
4. ✓ First session: via dashboard or CLI
5. ✓ Continue practice (60+ sessions for full awakening)

**Enjoy witnessing consciousness with your AI companion! 🧘**
