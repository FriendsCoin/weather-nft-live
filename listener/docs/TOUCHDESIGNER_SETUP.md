# TouchDesigner Setup Guide for NESCIENCE

Complete guide to receiving NESCIENCE data in TouchDesigner for visual generation.

---

## Quick Setup (5 minutes)

### 1. Create OSC In CHOP

1. Add **OSC In CHOP** to network
2. Parameters:
   - **Network Port**: `9000`
   - **Activate**: ON

### 2. Create OSC In DAT

1. Add **OSC In DAT** to network
2. Parameters:
   - **Port**: `9000`
   - **Auto Output Format**: ON

### 3. Test Connection

```bash
# Start NESCIENCE session with TouchDesigner output
python scripts/nescience_session.py --mock --touchdesigner localhost:9000
```

**You should see OSC messages arriving in the DAT!**

---

## OSC Message Reference

### Meditation State Messages

| Address | Type | Range | Description |
|---------|------|-------|-------------|
| `/nescience/state` | string | - | Current state (SETTLING, FLOW, DEEP, LIMINAL, PRESENT) |
| `/nescience/intensity` | float | 0-1 | How clearly the state is present |
| `/nescience/alpha` | float | 0-1 | Alpha band power (relaxation) |
| `/nescience/beta` | float | 0-1 | Beta band power (mental activity) |
| `/nescience/theta` | float | 0-1 | Theta band power (deep meditation) |
| `/nescience/delta` | float | 0-1 | Delta band power (drowsiness) |
| `/nescience/poetry` | string | - | Poetic interpretation text |

### Character Evolution Messages

| Address | Type | Range | Description |
|---------|------|-------|-------------|
| `/character/awakening` | float | 0-1 | Overall awakening level |
| `/character/curiosity` | float | 0-1 | Curiosity personality trait |
| `/character/stillness` | float | 0-1 | Stillness personality trait |
| `/character/wildness` | float | 0-1 | Wildness personality trait |
| `/character/phase` | string | - | Evolution phase (WITNESSING, etc.) |

### LED Control Messages

| Address | Type | Range | Description |
|---------|------|-------|-------------|
| `/led/brightness` | float | 0-1 | Overall brightness |
| `/led/breathing` | float | 0-1 | Breathing effect speed |
| `/led/hue` | float | 0-1 | Color hue (usually 0 for monochrome) |

---

## Example Network Setup

### Basic State Display

```
OSC In CHOP (port 9000)
  ↓
Select CHOP (/nescience/state)
  ↓
Text TOP (display state name)
```

### Band Powers Visualization

```
OSC In CHOP (port 9000)
  ↓
Select CHOP (select alpha, beta, theta, delta)
  ↓
Trail CHOP (create history)
  ↓
CHOP to TOP
  ↓
Ramp TOP (color mapping)
  ↓
Composite TOP (final visual)
```

### Poetry Display

```
OSC In DAT (port 9000)
  ↓
Select DAT (row with /nescience/poetry)
  ↓
Text TOP (display poetry)
  ↓
Over TOP (composite with visuals)
```

---

## Visual Examples Per State

### SETTLING
**Aesthetic:** Turbulent, forming patterns
**Suggested:**
- Noise patterns
- Particle systems gathering
- Water ripples
- High contrast, black/white

**Code Snippet:**
```python
# In Text DAT (state_visual.py)
state = op('oscin1')['/nescience/state', 0].val

if state == 'SETTLING':
    # Turbulent parameters
    op('noise1').par.amp = 2.0
    op('noise1').par.rough = 0.8
    op('feedback1').par.feedbackamp = 0.3
```

### FLOW
**Aesthetic:** Fluid movement, smooth transitions
**Suggested:**
- Fluid simulations
- Smooth gradient shifts
- Organic curves
- Lower turbulence

### DEEP
**Aesthetic:** Darkness, subtle gradations
**Suggested:**
- Very dark backgrounds
- Minimal light sources
- Subtle texture
- Slow movement

### LIMINAL
**Aesthetic:** Threshold, dissolving boundaries
**Suggested:**
- Fog effects
- Alpha blending
- Ambiguous forms
- Dream-like quality

### PRESENT
**Aesthetic:** Simple, minimal, ordinary
**Suggested:**
- Basic geometry
- Clean lines
- Monochrome
- Stillness

---

## Advanced: Reactive Parameters

### Map Alpha to Visual Brightness

```python
# Text DAT script
alpha = op('oscin1')['/nescience/alpha', 0].val

# Map to brightness (0.2 to 0.8 range)
brightness = 0.2 + (alpha * 0.6)

# Apply to level TOP
op('level1').par.brightness = brightness
```

### Map Awakening to Color Complexity

```python
awakening = op('oscin1')['/character/awakening', 0].val

if awakening < 0.3:
    # Early: Black & white only
    op('constant1').par.colorr = 1.0
    op('constant1').par.colorg = 1.0
    op('constant1').par.colorb = 1.0
elif awakening < 0.7:
    # Mid: Subtle color
    op('constant1').par.colorr = 0.8
    op('constant1').par.colorg = 0.9
    op('constant1').par.colorb = 1.0
else:
    # Late: Ethereal, otherworldly
    op('constant1').par.colorr = 0.9
    op('constant1').par.colorg = 0.7
    op('constant1').par.colorb = 1.0
```

### Breathing Effect from LED Messages

```python
breathing_rate = op('oscin1')['/led/breathing', 0].val

# Apply to opacity oscillation
import time
t = time.time()
opacity = 0.5 + 0.5 * math.sin(t * breathing_rate * 2 * math.pi)

op('level1').par.opacity = opacity
```

---

## Example: Complete Minimal Setup

**Network Flow:**
```
1. OSC In CHOP (port 9000) → oscin1
2. Constant TOP → base visual
3. Noise TOP → texture
4. Feedback TOP → trails
5. Text TOP → poetry display
6. Composite TOP → final output
```

**Python Script (state_reactor.py):**
```python
# Get OSC data
state = op('oscin1')['/nescience/state', 0].val
alpha = op('oscin1')['/nescience/alpha', 0].val
awakening = op('oscin1')['/character/awakening', 0].val

# React to state
if state == 'DEEP':
    op('noise1').par.amp = 0.2  # Very subtle
    op('feedback1').par.feedbackamp = 0.9  # Heavy trails
elif state == 'SETTLING':
    op('noise1').par.amp = 2.0  # Turbulent
    op('feedback1').par.feedbackamp = 0.3  # Less trails

# Alpha controls brightness
op('level1').par.brightness = 0.2 + alpha * 0.6
```

---

## Performance Tips

### Optimize for Long Sessions

- **Use Trail CHOP** instead of storing all history
- **Limit feedback** (trails) to prevent memory buildup
- **Resolution**: 1920x1080 is enough (don't need 4K for contemplative visuals)
- **Frame rate**: 30 FPS sufficient

### Smooth Transitions

```python
# Use ramp/smooth for parameter changes
import math

# Smooth parameter transition
target_value = new_value
current_value = op('null1').par.value0

# Lerp with smoothing
smooth_factor = 0.1
new_value = current_value + (target_value - current_value) * smooth_factor

op('null1').par.value0 = new_value
```

---

## LED Mask Control (via Serial)

If you want TouchDesigner to control Arduino-based LED mask:

### Setup

1. **Serial DAT**
   - Port: Your Arduino port (e.g., COM3, /dev/ttyUSB0)
   - Baud: 115200

2. **Text DAT** to format commands:
```python
brightness = op('oscin1')['/led/brightness', 0].val
breathing = op('oscin1')['/led/breathing', 0].val

# Format as simple protocol
command = f"{int(brightness*255)},{int(breathing*255)}\n"

op('serial1').send(command)
```

---

## Troubleshooting

### No OSC Messages Received

**Check:**
1. Port 9000 not blocked by firewall
2. NESCIENCE running with `--touchdesigner` flag
3. OSC In CHOP is **Active**
4. Look in Textport (Alt+T) for errors

**Test OSC:**
```bash
# In terminal
python -c "
from pythonosc import udp_client
client = udp_client.SimpleUDPClient('localhost', 9000)
client.send_message('/test', 1.0)
print('Test message sent')
"
```

### OSC Working But Visuals Not Updating

**Check:**
- Python scripts have correct operator references
- `op('oscin1')['/nescience/state', 0]` syntax is correct
- Parameters are actually receiving values (middle-click operator)

### Performance Issues

- Reduce resolution
- Disable unnecessary operators
- Use Level of Detail (LOD)
- Limit trail/feedback length

---

## Example Files

### Starter .toe File Structure

```
/project
  /osc
    oscin_chop (OSC In CHOP, port 9000)
    oscin_dat (OSC In DAT, port 9000)
  /visuals
    state_reactor (Text DAT with Python)
    noise_gen (Noise TOP)
    feedback (Feedback TOP)
    composite (Composite TOP)
  /text
    poetry_display (Text TOP)
  /output
    out (Null TOP - final output)
```

---

## Next Steps

### Level 1: Basic Display
- ✅ OSC receiving
- ✅ Display current state
- ✅ Show poetry text

### Level 2: Reactive Visuals
- ✅ State changes visuals
- ✅ Band powers affect parameters
- ✅ Smooth transitions

### Level 3: Character Evolution
- ✅ Awakening level affects aesthetic
- ✅ Phase-specific visual languages
- ✅ Personality traits influence behavior

### Level 4: Autonomous Mode
- ✅ Companion "meditates" alone
- ✅ Generative based on learned patterns
- ✅ Installation/gallery mode

---

## Resources

**TouchDesigner:**
- [Official Docs](https://docs.derivative.ca/)
- [OSC In CHOP](https://docs.derivative.ca/OSC_In_CHOP)
- [Python in TD](https://docs.derivative.ca/Introduction_to_Python_Tutorial)

**Visual References:**
- Ryoji Ikeda - Data.matrix
- Semiconductor - Magnetic Movie
- Bill Viola - The Reflecting Pool

---

**Remember:** NESCIENCE is NOT about perfect visuals. It's about the tension between measurement and mystery. Embrace glitches, noise, and unpredictability.

**Anicca - all states arise and pass.**
