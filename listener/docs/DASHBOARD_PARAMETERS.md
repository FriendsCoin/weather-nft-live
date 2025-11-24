# Dashboard Parameter Configuration Guide

Complete reference for configurable parameters in the NESCIENCE Dashboard Hub.

## Overview

The NESCIENCE Dashboard Hub (`http://localhost:8080`) provides **modal-based parameter configuration** for all scripts. Each action opens a modal dialog where you can customize parameters before launching.

This enables both:
- ✓ **Modular CLI execution** - Run any script independently with custom parameters
- ✓ **Dashboard execution** - Configure and launch via web interface with same parameters

---

## Meditation Session Parameters

### Modal: 🧘 Start Meditation Session

**Available Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **Mock Data** | Checkbox | ✓ Checked | Use mock EEG data (testing without hardware) |
| **Duration** | Number | 600 | Session length in seconds (60-7200) |
| **Visualize** | Checkbox | ✗ Unchecked | Enable native matplotlib visualization |
| **TouchDesigner** | Checkbox + Text | localhost:9000 | Send OSC to TouchDesigner for visuals |

### CLI Equivalent

```bash
# Via dashboard modal (automatic)
# Click "Start Meditation Session" → Configure → Start

# Via CLI (manual)
python scripts/nescience_session.py \
    --duration 1200 \
    --mock \
    --visualize \
    --touchdesigner localhost:9000
```

### API Payload

```json
{
  "mock": true,
  "duration": 1200,
  "visualize": true,
  "touchdesigner": "localhost:9000"
}
```

### Use Cases

**Development/Testing:**
```
✓ Mock Data
Duration: 300 (5 min)
✓ Visualize
```

**Personal Practice (with visualization):**
```
✗ Mock Data (real Muse S)
Duration: 1200 (20 min)
✓ Visualize
```

**Live Performance:**
```
✗ Mock Data
Duration: 1800 (30 min)
✗ Visualize
✓ TouchDesigner (localhost:9000)
```

---

## Baseline Calibration Parameters

### Modal: 🎯 Calibrate Baseline

**Available Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **Mock Data** | Checkbox | ✓ Checked | Use mock EEG data for testing |
| **Duration** | Number | 600 | Calibration time in seconds (300-1200) |

### CLI Equivalent

```bash
# Via dashboard
# Click "Calibrate Baseline" → Configure → Start

# Via CLI
python scripts/calibrate_baseline.py \
    --duration 600 \
    --mock
```

### API Payload

```json
{
  "mock": false,
  "duration": 600
}
```

### Recommendations

**First calibration (real hardware):**
```
✗ Mock Data
Duration: 600 (10 min quiet sitting)
```

**Testing calibration logic:**
```
✓ Mock Data
Duration: 300 (5 min test)
```

---

## Autonomous Meditation Parameters

### Modal: 🎭 Autonomous Mode (Gallery)

**Available Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **TouchDesigner** | Checkbox + Text | localhost:9000 | OSC address for visuals |
| **Update Rate** | Number | 2.0 | State updates per second (0.5-10 Hz) |

**Requirements:**
- COMPANIONSHIP phase (60+ sessions)
- 80%+ awakening level
- Button disabled until requirements met

### CLI Equivalent

```bash
# Via dashboard (when enabled)
# Click "Autonomous Mode" → Configure → Start

# Via CLI
python scripts/autonomous_meditation.py \
    --touchdesigner localhost:9000 \
    --update-rate 2.0
```

### API Payload

```json
{
  "touchdesigner": "localhost:9000",
  "update_rate": 2.0
}
```

### Use Cases

**Gallery installation (slow drift):**
```
✓ TouchDesigner (localhost:9000)
Update Rate: 0.5 Hz (slow, contemplative)
```

**Performance (responsive):**
```
✓ TouchDesigner (localhost:9000)
Update Rate: 5.0 Hz (real-time reactive)
```

---

## OSC Connection Test Parameters

### Modal: 🔌 Test OSC Connection

**Available Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **Mode** | Select | Receive | Receive (Mind Monitor) or Send (TouchDesigner) |
| **Port** | Number | 5000 | Port number (auto-updates: 5000/9000) |
| **Host** | Text | localhost | Target host (only for Send mode) |

**Note:** This modal displays CLI command - execution is manual in terminal.

### CLI Examples

```bash
# Test Mind Monitor (receive)
python scripts/test_osc.py --receive --port 5000

# Test TouchDesigner (send)
python scripts/test_osc.py --send --host localhost --port 9000
```

---

## Character Visualization

### Button: 📊 Visualize Character

**No parameters** - This action displays a CLI command.

**CLI Command:**
```bash
python scripts/visualize_character.py
```

Creates matplotlib charts showing:
- Awakening progress over sessions
- Phase transitions
- Personality trait evolution

---

## Architecture: Parameter Flow

### Dashboard → API → Script

```
┌─────────────────────────────────────────────────────────┐
│  1. User clicks action button                           │
│     └─> Modal opens with parameter forms                │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  2. User configures parameters                           │
│     - Toggles checkboxes                                 │
│     - Adjusts numbers                                    │
│     - Enters text values                                 │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  3. User clicks "Start" in modal                         │
│     └─> JavaScript collects form values                 │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  4. AJAX POST to Flask API                               │
│     - POST /api/start_session                            │
│     - POST /api/calibrate                                │
│     - POST /api/start_autonomous                         │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  5. Flask server builds command                          │
│     cmd = ['python', 'script.py', '--param', value]     │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  6. subprocess.Popen() launches script                   │
│     - Runs in background                                 │
│     - Returns immediately                                │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│  7. Script runs with configured parameters               │
│     - Same behavior as manual CLI launch                 │
└─────────────────────────────────────────────────────────┘
```

### Example: Starting Session with Visualization

**Dashboard UI:**
```
Modal: Start Meditation Session
├─ ✓ Mock Data
├─ Duration: 600
├─ ✓ Visualize
└─ ✗ TouchDesigner
   Click [Start Session]
```

**JavaScript (frontend):**
```javascript
fetch('/api/start_session', {
    method: 'POST',
    body: JSON.stringify({
        mock: true,
        duration: 600,
        visualize: true,
        touchdesigner: null
    })
})
```

**Python (backend):**
```python
cmd = ['python', 'scripts/nescience_session.py']
cmd.extend(['--duration', '600'])
cmd.append('--mock')
cmd.append('--visualize')
subprocess.Popen(cmd)
```

**Executed command:**
```bash
python scripts/nescience_session.py --duration 600 --mock --visualize
```

---

## Modular Execution Patterns

### Pattern 1: Dashboard Only

**Use Case:** Non-technical users, visual interface preference

```
1. Start dashboard: python start_dashboard.py
2. Open browser: http://localhost:8080
3. Click action buttons
4. Configure in modals
5. Launch sessions
```

**Advantages:**
- ✓ Visual feedback
- ✓ No CLI knowledge needed
- ✓ Session history
- ✓ Character state monitoring

---

### Pattern 2: CLI Only

**Use Case:** Developers, automation, scripting

```bash
# Session
python scripts/nescience_session.py --duration 1200 --visualize

# Calibration
python scripts/calibrate_baseline.py --duration 600 --mock

# Autonomous
python scripts/autonomous_meditation.py --touchdesigner localhost:9000
```

**Advantages:**
- ✓ Scriptable
- ✓ CI/CD integration
- ✓ No browser required
- ✓ Direct control

---

### Pattern 3: Hybrid (RECOMMENDED)

**Use Case:** Development, performance, research

```
Terminal 1: Dashboard (monitoring)
    python start_dashboard.py
    → http://localhost:8080

Terminal 2: Direct CLI execution (testing)
    python scripts/nescience_session.py --mock --visualize

Browser: Monitor character state and session history
```

**Advantages:**
- ✓ Best of both worlds
- ✓ Dashboard for monitoring
- ✓ CLI for rapid iteration
- ✓ Visual + programmatic control

---

## API Endpoints Summary

All parameter-configured endpoints:

### POST /api/start_session
**Parameters:**
- `mock` (boolean)
- `duration` (integer)
- `visualize` (boolean)
- `touchdesigner` (string or null)

**Returns:** `{status: 'started', command: '...'}`

---

### POST /api/calibrate
**Parameters:**
- `mock` (boolean)
- `duration` (integer)

**Returns:** `{status: 'started', command: '...'}`

---

### POST /api/start_autonomous
**Parameters:**
- `touchdesigner` (string or null)
- `update_rate` (float)

**Validation:**
- Checks character phase and awakening level
- Returns 400 error if requirements not met

**Returns:** `{status: 'started', command: '...'}`

---

### GET /api/status
**Returns:**
```json
{
  "character": {
    "phase": "WITNESSING",
    "awakening_level": 0.15,
    "total_sessions": 8,
    "total_hours": 2.5,
    "personality": {...},
    "can_meditate_alone": false
  },
  "baseline": {
    "calibrated": false,
    "message": "..."
  }
}
```

---

### GET /api/sessions
**Returns:**
```json
{
  "sessions": [
    {
      "id": "session_012",
      "date": "2025-01-15",
      "duration": 720,
      "states": ["FLOW", "DEEP"],
      "awakening_delta": 0.02
    }
  ]
}
```

---

## Testing Parameter Configuration

### Test 1: Modal Opens and Closes
```
1. Click "Start Meditation Session"
2. Verify modal opens
3. Click X or Cancel
4. Verify modal closes
```

### Test 2: Parameter Defaults
```
1. Open session modal
2. Verify defaults:
   - Mock: ✓ checked
   - Duration: 600
   - Visualize: ✗ unchecked
   - TouchDesigner: ✗ unchecked, "localhost:9000"
```

### Test 3: Parameter Modification
```
1. Open session modal
2. Change duration to 1200
3. Check visualize
4. Uncheck mock
5. Start session
6. Verify command in feedback: "1200s, real, visualized"
```

### Test 4: TouchDesigner Address
```
1. Open session modal
2. Check TouchDesigner
3. Change address to "192.168.1.100:9000"
4. Start session
5. Verify command includes: --touchdesigner 192.168.1.100:9000
```

### Test 5: CLI Equivalence
```bash
# Dashboard: mock=true, duration=600, visualize=true
# Should produce:

python scripts/nescience_session.py --duration 600 --mock --visualize

# Test CLI directly with same params:
python scripts/nescience_session.py --duration 600 --mock --visualize

# Behavior should be identical
```

---

## Troubleshooting

### Modal doesn't open
**Check:** JavaScript console for errors
**Fix:** Ensure jQuery/socket.io loaded

### Parameters not passed to script
**Check:** Network tab in browser dev tools
**Fix:** Verify JSON payload in POST request

### Script doesn't start
**Check:** Dashboard feedback message
**Fix:** Verify Python path, script permissions

### CLI works but dashboard doesn't
**Check:** Command string in API response
**Fix:** Compare with manual CLI command

---

## Summary

**The NESCIENCE Dashboard Hub provides:**

1. ✓ **Modal-based configuration** - Visual parameter editing
2. ✓ **Full CLI equivalence** - Same parameters available in terminal
3. ✓ **Modular execution** - Launch scripts independently or via dashboard
4. ✓ **Flexible workflow** - Use dashboard, CLI, or both simultaneously
5. ✓ **Parameter validation** - Form validation and server-side checks

**Every parameter available via dashboard is also available via CLI.**

**Every script can run independently or be launched through the dashboard.**

**This enables rapid iteration, automation, and user-friendly interfaces simultaneously.**

---

**Next Steps:**

1. Start dashboard: `python start_dashboard.py`
2. Open browser: `http://localhost:8080`
3. Try launching sessions with different parameters
4. Compare with CLI execution
5. Use whichever method fits your workflow

**Modular. Configurable. Flexible.** 🚀
