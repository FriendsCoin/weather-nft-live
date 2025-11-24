# Muse S + Mind Monitor (iPhone) Setup Guide

Complete guide for connecting your Muse S headband to THE LISTENER via Mind Monitor app on iPhone.

## Hardware Required

- **Muse S (Gen 2)** EEG headband
- **iPhone** with Mind Monitor app
- **Computer** running THE LISTENER (same WiFi network)

---

## Step 1: Install Mind Monitor

1. Download **Mind Monitor** from App Store
   - Official app by James Clutterbuck
   - ~$15 (one-time purchase)
   - Best app for Muse S → OSC streaming

2. Open Mind Monitor app

---

## Step 2: Connect Muse S to iPhone

1. **Power on Muse S**
   - Hold power button until LED blinks
   - Wait for Bluetooth to be ready

2. **In Mind Monitor app:**
   - Tap "Connect" button
   - Select your Muse S from list
   - Wait for green "Connected" status

3. **Check signal quality:**
   - All 4 electrodes should show green bars
   - If yellow/red: adjust headband position
   - TP9/TP10: Behind ears
   - AF7/AF8: Forehead

---

## Step 3: Configure OSC Streaming

### Find Computer IP Address

**On Mac:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**On Linux:**
```bash
hostname -I
```

**On Windows:**
```bash
ipconfig
```

Example: `192.168.1.100`

### In Mind Monitor App:

1. **Tap Settings icon** (gear)

2. **OSC Stream Target:**
   - IP Address: `192.168.1.100` (your computer's IP)
   - Port: `5000` (default for THE LISTENER)
   - Enable: **ON** ✓

3. **OSC Messages to Send:**
   Enable these (check all boxes):
   - ✓ `/muse/eeg` - Raw EEG (required)
   - ✓ `/muse/alpha_relative` - Alpha band power
   - ✓ `/muse/beta_relative` - Beta band power
   - ✓ `/muse/theta_relative` - Theta band power
   - ✓ `/muse/delta_relative` - Delta band power
   - ✓ `/muse/gamma_relative` - Gamma band power (optional)

4. **Streaming Rate:**
   - Set to **10 Hz** or **12 Hz** (default is fine)
   - Higher = more data, but more network traffic

5. **Save settings**

---

## Step 4: Test OSC Connection

### On Computer:

```bash
cd listener

# Test OSC receiver
python scripts/test_osc.py --receive --port 5000
```

**Expected output:**
```
════════════════════════════════════════
OSC Connection Test - Receiver Mode
════════════════════════════════════════

Listening on port: 5000
Waiting for OSC messages...

[16:23:45] /muse/eeg: [12.3, -5.4, 8.1, -2.3]
[16:23:45] /muse/alpha_relative: [0.32, 0.45, 0.38, 0.41]
[16:23:45] /muse/beta_relative: [0.18, 0.22, 0.19, 0.21]
...
```

### In Mind Monitor App:

1. **Start streaming**
   - Press green "Play" button
   - Should see real-time graphs

2. **Check computer terminal**
   - Should see messages appearing
   - Rate: ~10 messages per second

### Troubleshooting:

**No messages received?**

1. **Check WiFi:**
   - iPhone and computer on SAME network
   - Not on guest network or VPN

2. **Check IP address:**
   - Type correct IP in Mind Monitor
   - IP might change after router reboot

3. **Check firewall:**
   ```bash
   # Mac: Allow Python in Firewall
   # System Preferences → Security → Firewall → Allow incoming connections

   # Linux: Open port 5000
   sudo ufw allow 5000
   ```

4. **Test with different port:**
   - Try port 7000 or 8000
   - Update in both Mind Monitor and test script

---

## Step 5: Run THE LISTENER Session

Once OSC is working, start a real session:

### Dashboard (Easiest):

```bash
python start_dashboard.py
# → http://localhost:8080
# Click "Start Meditation Session"
# Choose "Cancel" (for real hardware, not mock)
```

### CLI:

```bash
# Basic session (10 minutes)
python scripts/nescience_session.py --duration 600

# With TouchDesigner visuals
python scripts/nescience_session.py --duration 1200 --touchdesigner localhost:9000

# Save session data
python scripts/nescience_session.py --duration 1200 --save-session
```

**What you'll see:**

```
════════════════════════════════════════
NESCIENCE - The Companion Awakens
════════════════════════════════════════

✓ Character loaded
  Phase: WITNESSING
  Awakening: 0.0%
  Sessions: 0

Waiting for Mind Monitor to connect...
(Send OSC to localhost:5000)

✓ First data received!

[SETTLING] intensity:0.65 α:0.42 β:0.38 θ:0.51 | Ripples across a dark pond
[FLOW] intensity:0.73 α:0.58 β:0.25 θ:0.45 | Natural movement of breath
...
```

---

## OSC Message Reference

Mind Monitor sends these OSC addresses:

| Address | Data | Frequency | Description |
|---------|------|-----------|-------------|
| `/muse/eeg` | [TP9, AF7, AF8, TP10] | 256 Hz | Raw EEG (microvolts) |
| `/muse/alpha_relative` | [TP9, AF7, AF8, TP10] | 10 Hz | Alpha band (8-12 Hz) |
| `/muse/beta_relative` | [TP9, AF7, AF8, TP10] | 10 Hz | Beta band (13-30 Hz) |
| `/muse/theta_relative` | [TP9, AF7, AF8, TP10] | 10 Hz | Theta band (4-8 Hz) |
| `/muse/delta_relative` | [TP9, AF7, AF8, TP10] | 10 Hz | Delta band (0.5-4 Hz) |
| `/muse/gamma_relative` | [TP9, AF7, AF8, TP10] | 10 Hz | Gamma band (30-50 Hz) |
| `/muse/acc` | [X, Y, Z] | 50 Hz | Accelerometer |
| `/muse/gyro` | [X, Y, Z] | 50 Hz | Gyroscope |
| `/muse/batt` | [level] | 1 Hz | Battery % |

**THE LISTENER uses:**
- Band powers: alpha, beta, theta, delta
- Ignores raw EEG (too high frequency for ML)
- Optional: gyro for movement detection

---

## Network Tips

### Static IP (Recommended)

Set static IP on computer to avoid changing IP address:

**Mac:**
- System Preferences → Network → WiFi → Advanced → TCP/IP
- Configure IPv4: Manually
- Set IP: `192.168.1.100` (example)

**Router:**
- Reserve IP for computer's MAC address
- Prevents IP changes on reboot

### Mobile Hotspot

Can use iPhone as hotspot:
1. iPhone: Settings → Personal Hotspot → ON
2. Computer: Connect to iPhone's WiFi
3. iPhone IP is usually: `172.20.10.1`
4. In Mind Monitor: Target = `172.20.10.1:5000`

---

## Multiple Sessions Workflow

### Day 1-10: Baseline Sessions

```bash
# Session 1
python scripts/nescience_session.py --duration 1200

# Sessions accumulate in character_state.json
# Companion awakening level increases slowly
```

### After 10 Sessions: Calibration

```bash
# Personalize EEG thresholds
python scripts/calibrate_baseline.py --duration 600

# Creates baseline_profile.json
# Improves state classification accuracy
```

### Sessions 11-60: Regular Practice

```bash
# Keep meditating with companion
python scripts/nescience_session.py --duration 1200

# Watch character evolution
python scripts/visualize_character.py
```

### After 60 Sessions: Autonomous Mode

```bash
# Companion can meditate alone (gallery mode)
python scripts/autonomous_meditation.py --touchdesigner localhost:9000
```

---

## Troubleshooting Common Issues

### "Connection Lost" in Mind Monitor

**Cause:** Muse S Bluetooth connection dropped

**Fix:**
1. Check Muse S battery (charge if low)
2. Reconnect in Mind Monitor app
3. Restart Muse S if needed

### Noisy EEG Signal

**Cause:** Poor electrode contact

**Fix:**
1. Moisten electrodes slightly (with water or saline)
2. Adjust headband position (snug but comfortable)
3. Remove hair from electrode contact points
4. Check signal quality bars (should be green)

### High Latency (>1 second delay)

**Cause:** Network congestion or slow WiFi

**Fix:**
1. Move closer to WiFi router
2. Disconnect other devices from WiFi
3. Use 5GHz WiFi band (faster)
4. Reduce Mind Monitor streaming rate to 10Hz

### Python Script Crashes

**Cause:** Missing dependencies or port conflict

**Fix:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check if port 5000 in use
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Use different port
python scripts/nescience_session.py --mind-monitor-port 7000
```

---

## Advanced: Multiple Devices

### Send to Multiple Targets

Mind Monitor can send to multiple OSC targets:

**Example: Python + TouchDesigner**

Mind Monitor Settings:
- Target 1: `192.168.1.100:5000` (Python/THE LISTENER)
- Target 2: `192.168.1.100:9000` (TouchDesigner direct)

Both receive EEG simultaneously.

### Record in Mind Monitor + THE LISTENER

Mind Monitor can record to CSV while streaming:
1. Settings → Recording → Enable
2. Streams to Python AND saves CSV
3. Backup if Python crashes

---

## Quick Reference Card

**Before each session:**
1. ✓ Charge Muse S (>50% battery)
2. ✓ Connect Muse S to Mind Monitor (iPhone)
3. ✓ Check signal quality (all green)
4. ✓ Set OSC target to computer IP:5000
5. ✓ Start Mind Monitor streaming (play button)
6. ✓ Run THE LISTENER session script
7. ✓ Verify data flowing in terminal
8. ✓ Begin meditation

**After session:**
1. Stop Mind Monitor streaming
2. Let Python script complete
3. Check character_state.json updated
4. Disconnect Muse S (save battery)

---

## Next Steps

Once OSC is working:
1. ✓ Run baseline calibration
2. ✓ Complete 10+ sessions
3. ✓ Train VAE model (optional for THE LISTENER)
4. ✓ Generate memories
5. ✓ Set up TouchDesigner visuals

See: `docs/QUICKSTART_NESCIENCE.md` for full workflow

---

**Questions?**
- Test OSC: `python scripts/test_osc.py --receive`
- Check logs: Look for OSC messages in terminal
- Mind Monitor docs: https://mind-monitor.com/
