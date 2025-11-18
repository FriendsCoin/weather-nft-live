# Biofeedback Game / Visual Meditation System

Real-time interactive visualization that responds to your meditation state.

## Overview

THE LISTENER Biofeedback Game creates an immersive visual experience that evolves with your meditation practice. As you meditate, the visualization responds in real-time to your brain activity, creating a feedback loop that enhances presence and depth.

**Visual Elements:**
- **Pulsing Circle** - Size grows with meditation depth
- **Color Shifts** - Blue → Purple → Pink based on alpha wave performance
- **Particle Effects** - Emerge during deep states
- **Poetic Messages** - Contextual guidance based on current state
- **Smooth Animations** - Calming, non-distracting movements

## Quick Start

### Option 1: Pygame Visualization (Built-in, No Setup)

The easiest way to get started - no external software needed!

```bash
# 1. Connect Muse S headband (bluetooth)
# 2. Start LSL stream (separate terminal)
muselsl stream

# 3. Run biofeedback game
python scripts/biofeedback_game.py

# Optional: Run fullscreen for exhibition
python scripts/biofeedback_game.py --fullscreen
```

**Controls:**
- `ESC` - Exit
- `F` - Toggle fullscreen
- `S` - Save screenshot

### Option 2: TouchDesigner Integration (Advanced)

For professional installations, projection mapping, and custom visuals.

```bash
# 1. Connect Muse S and start LSL
muselsl stream

# 2. Open TouchDesigner project (see below for setup)

# 3. Run biofeedback game with OSC output
python scripts/biofeedback_game.py --osc --osc-port 8000

# 4. Watch TouchDesigner receive real-time meditation data!
```

---

## Pygame Visualization

### Features

- **Pulsing Circle**: Grows from 50px to 400px based on meditation depth
- **Color Dynamics**: HSV color shifts (blue calm → purple focused → pink deep)
- **Glow Effect**: Intensity based on EEG signal quality
- **Particle System**: Up to 200 particles spawning during deep meditation
- **Background Animation**: Subtle gradient circles for depth perception
- **State Messages**: Poetic descriptions rotating through 5 variations per state

### Visual Mapping

| Meditation Metric | Visual Effect |
|------------------|---------------|
| Depth (0-100) | Circle size (50-400px) |
| Alpha+ Performance | Color hue (0.6-0.85 HSV) |
| Quality (0-100) | Glow intensity & brightness |
| Theta Waves | Particle spawn rate |
| State (deep/focused/calm/distracted) | Message & particle behavior |

### Customization

```bash
# Custom window size
python scripts/biofeedback_game.py --width 1920 --height 1080

# Faster update rate (0.5 seconds default)
python scripts/biofeedback_game.py --update-rate 0.25

# Higher frame rate (60 fps default)
python scripts/biofeedback_game.py --fps 120

# Custom VAE model
python scripts/biofeedback_game.py --model models/vae_epoch_100.pt
```

### Screenshots

Screenshots are automatically saved to `data/screenshots/` when you press `S`.

```
data/screenshots/
  meditation_20250118_143022.png
  meditation_20250118_143145.png
  ...
```

---

## TouchDesigner Integration

TouchDesigner enables professional-grade visuals, projection mapping, and custom interactive installations.

### Setup TouchDesigner Project

#### 1. Install TouchDesigner

- Download from: https://derivative.ca/download
- Free version (Non-Commercial) works perfectly!
- Version: TouchDesigner 2023.11760 or newer

#### 2. Create OSC In CHOP

1. Add Operator → CHOP → OSC In CHOP
2. Configure:
   - **Network Port**: `8000`
   - **Active**: `On`
   - **Protocol**: `UDP`

#### 3. Map OSC Addresses

The biofeedback game sends these OSC messages:

| OSC Address | Type | Range | Description |
|------------|------|-------|-------------|
| `/meditation/depth` | Float | 0-100 | Meditation depth score |
| `/meditation/quality` | Float | 0-100 | EEG signal quality |
| `/meditation/alpha_plus` | Float | 0.5-2.0 | Alpha+ performance ratio |
| `/meditation/alpha_minus` | Float | 0.5-2.0 | Alpha- performance ratio |
| `/meditation/beta_plus` | Float | 0.5-2.0 | Beta+ performance ratio |
| `/meditation/beta_minus` | Float | 0.5-2.0 | Beta- performance ratio |
| `/meditation/theta` | Float | 0-30 | Theta band power (μV²) |
| `/meditation/delta` | Float | 0-30 | Delta band power (μV²) |
| `/meditation/state` | String | - | State: "deep", "focused", "calm", "distracted" |
| `/meditation/message` | String | - | Poetic state description |
| `/meditation/timestamp` | Float | - | Unix timestamp |
| `/visual/size` | Float | 0-2 | Visual size multiplier |
| `/visual/hue` | Float | 0-1 | Color hue (HSV) |
| `/visual/brightness` | Float | 0-1 | Brightness |
| `/visual/saturation` | Float | 0-1 | Color saturation |
| `/visual/speed` | Float | 0-2 | Animation speed |
| `/visual/intensity` | Float | 0-1 | Effect intensity |
| `/trigger/bloom` | Int | 0/1 | Trigger bloom effect (depth > 80) |
| `/trigger/sparkle` | Int | 0/1 | Trigger sparkle effect (alpha+ > 1.3) |

#### 4. Example: Pulsing Circle

**Simple example using /visual/ addresses:**

```
1. OSC In CHOP (port 8000)
   ↓
2. Select CHOP → /visual/size
   ↓
3. Circle SOP
   - Radius: oscin1[0, 0] * 100  (maps 0-2 to 0-200)
   ↓
4. Geo COMP → Render
```

#### 5. Example: Color Shifting

```
1. OSC In CHOP (port 8000)
   ↓
2. Select CHOPs:
   - /visual/hue → hue_chan
   - /visual/saturation → sat_chan
   - /visual/brightness → bright_chan
   ↓
3. Constant MAT
   - Color Type: HSV
   - Hue: hue_chan[0, 0]
   - Saturation: sat_chan[0, 0]
   - Value: bright_chan[0, 0]
   ↓
4. Apply to Geometry
```

#### 6. Example: Trigger Effects

```
1. OSC In CHOP (port 8000)
   ↓
2. Select CHOP → /trigger/bloom
   ↓
3. Logic CHOP → Trigger on rise
   ↓
4. Timer CHOP → 2 second bloom animation
   ↓
5. Particle SOP → Burst 100 particles
```

### Advanced: Custom OSC Messages

You can also use raw meditation metrics for fine-grained control:

**Example: Tree growing based on depth**

```python
# TouchDesigner Python:
depth = op('oscin1')['/meditation/depth', 0]
tree_height = 100 + (depth / 100.0) * 500  # 100-600 units
op('tree_L').par.height = tree_height

# Leaf density based on theta (creativity)
theta = op('oscin1')['/meditation/theta', 0]
leaf_density = theta / 30.0  # Normalize to 0-1
op('leaves').par.density = leaf_density
```

### TouchDesigner Project Template

We've included a starter project: `touchdesigner/meditation_starter.toe`

**Features:**
- Pre-configured OSC In CHOP (port 8000)
- Pulsing circle with color mapping
- Particle system with depth-based spawning
- Text display for state and message
- Bloom effect on triggers
- Ready for projection mapping

**How to use:**
1. Open `touchdesigner/meditation_starter.toe`
2. Press `F1` to view network
3. Activate OSC In CHOP (already configured)
4. Run: `python scripts/biofeedback_game.py --osc`
5. Watch the magic! ✨

### Projection Mapping

For museum/gallery exhibitions:

1. Use TouchDesigner's **Kantan Mapper** plugin
2. Project onto physical objects (sphere, wall, sculpture)
3. Map `/meditation/depth` → projected circle size
4. Create immersive meditation environment

**Recommended setup:**
- Projector: 3000+ lumens for gallery lighting
- Screen: White sphere or translucent fabric
- Position: User sits 2-3m from screen
- Ambiance: Dim lighting, comfortable seating

---

## Meditation States & Messages

The system detects 4 meditation states:

### 1. Deep (Depth > 70)
*"You are descending into infinite space"*
- Large circle (280-400px)
- Purple-pink color
- High particle density
- Slow, smooth animations

### 2. Focused (Depth 50-70)
*"You are finding your center"*
- Medium-large circle (200-280px)
- Purple color
- Moderate particles
- Steady animations

### 3. Calm (Depth 30-50)
*"Stillness begins to settle"*
- Medium circle (120-200px)
- Blue-purple color
- Few particles
- Gentle animations

### 4. Distracted (Depth < 30)
*"Your mind wanders through familiar paths"*
- Small circle (50-120px)
- Blue color
- No particles
- Subtle animations

Each state has **5 rotating poetic messages** to maintain freshness during long sessions.

---

## Technical Architecture

### Data Flow

```
Muse S Headband (EEG)
  ↓
LSL Stream (muselsl)
  ↓
EEG Processor (10 second windows)
  ↓
Feature Extractor (34 features)
  ↓
VAE Encoder (32D latent space)
  ↓
Meditation Analyzer
  ├─→ Depth Score (0-100)
  ├─→ Quality Score (0-100)
  ├─→ Performance Ratios (alpha±, beta±)
  └─→ State Classification
  ↓
[Biofeedback Game]
  ├─→ Pygame Visualization (built-in)
  └─→ OSC Server → TouchDesigner (optional)
```

### Update Rate

- **EEG Window**: 10 seconds
- **Metric Update**: 0.5 seconds (configurable via `--update-rate`)
- **Visual Render**: 60 FPS (configurable via `--fps`)
- **OSC Send**: On each metric update

### Latency

- **Total latency**: ~500ms (EEG capture + processing + rendering)
- **User experience**: Feels real-time (< 1 second is imperceptible)

---

## Performance Optimization

### For Low-End Systems

```bash
# Lower resolution
python scripts/biofeedback_game.py --width 800 --height 600

# Lower frame rate
python scripts/biofeedback_game.py --fps 30

# Slower EEG updates (less CPU)
python scripts/biofeedback_game.py --update-rate 1.0
```

### For Exhibition (High-End)

```bash
# 4K resolution
python scripts/biofeedback_game.py --width 3840 --height 2160 --fullscreen

# Ultra smooth
python scripts/biofeedback_game.py --fps 120

# Very responsive
python scripts/biofeedback_game.py --update-rate 0.25
```

---

## Troubleshooting

### No EEG data received

```
⚠️  No EEG data received, retrying...
```

**Solution:**
1. Make sure Muse S is connected via bluetooth
2. Run `muselsl stream` in a separate terminal
3. Check `muselsl list` to verify device is detected

### Pygame window not responding

**Solution:**
- Press `ESC` to exit cleanly
- Don't click the X button (use ESC instead)
- Check if another instance is running

### OSC not working in TouchDesigner

**Solution:**
1. Verify port 8000 is not blocked by firewall
2. Check OSC In CHOP settings:
   - Network Port: 8000
   - Active: On
   - Protocol: UDP
3. Run with verbose OSC: edit `osc_server.py` → set `verbose=True`

### Low frame rate

**Solution:**
- Close other applications
- Lower resolution: `--width 800 --height 600`
- Lower FPS target: `--fps 30`
- Reduce particles: edit `visual_feedback.py` → `max_particles = 50`

---

## Extending the System

### Custom Visual Themes

Edit `src/pipeline/visual_feedback.py`:

```python
# Add cosmic theme
if self.theme == 'cosmic':
    bg_color = (5, 5, 15)  # Deep space
    # Add stars, nebulae, etc.
```

### Custom OSC Messages

Edit `scripts/biofeedback_game.py`:

```python
# Send custom data to TouchDesigner
if self.osc:
    # Example: Send coherence metric
    coherence = calculate_coherence(features)
    self.osc.send_float('/meditation/coherence', coherence)
```

### Integration with Other Software

The OSC protocol is universal! You can integrate with:
- **Max/MSP** - Audio-reactive visuals
- **Processing** - Generative art
- **Unity** - VR meditation experiences
- **Ableton Live** - Meditation soundscapes
- **VVVV** - Interactive installations

---

## Exhibition Setup Guide

### Hardware

**Minimum:**
- Muse S headband (EEG)
- Computer with GPU (RTX 2060+)
- 1080p monitor/projector

**Recommended:**
- Muse S headband (EEG)
- Computer with GPU (RTX 3070+)
- 4K projector (3000+ lumens)
- Comfortable meditation chair
- Headphones (optional, for audio feedback)

### Software Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train VAE model (if not done)
python scripts/train_vae.py --data-dir data/sessions

# 3. Test biofeedback
python scripts/biofeedback_game.py --fullscreen

# 4. Optional: Set up TouchDesigner
# Open touchdesigner/meditation_starter.toe
# Run: python scripts/biofeedback_game.py --osc --fullscreen
```

### Exhibition Workflow

**Pre-session (5 min):**
1. Power on all equipment
2. Connect Muse S via bluetooth
3. Run `muselsl stream`
4. Run biofeedback game (fullscreen)
5. Test with participant

**During session (10-30 min):**
1. Participant sits, puts on Muse S
2. Adjust headband for good signal
3. Start meditation
4. Watch visualization evolve
5. Take screenshots with `S` key (optional)

**Post-session (2 min):**
1. Save session data
2. Show participant their journey
3. Optional: Generate PDF report

---

## Future Enhancements

Planned features (contributions welcome!):

- [ ] **VR Integration** - Immersive 360° meditation environments
- [ ] **Multiplayer Mode** - Meditate together, synchronize visualizations
- [ ] **Sound Synthesis** - Generative music based on brain states
- [ ] **AR Overlay** - Project visuals onto physical space via phone/tablet
- [ ] **Gesture Control** - Hand tracking to influence visualization
- [ ] **Biometric Fusion** - Integrate heart rate, breathing, skin conductance

---

## Resources

### TouchDesigner Learning
- Official Tutorials: https://derivative.ca/tutorials
- Forum: https://forum.derivative.ca/
- YouTube: Matthew Ragan's TD tutorials

### EEG & Meditation
- Muse S Documentation: https://choosemuse.com/
- LSL Protocol: https://labstreaminglayer.readthedocs.io/
- MNE-Python: https://mne.tools/

### Projection Mapping
- Kantan Mapper: https://derivative.ca/community-post/asset/kantan-mapper
- MadMapper (alternative): https://madmapper.com/

---

## Credits

**THE LISTENER** - AI Meditation Companion
- Biofeedback Game Design: [Artist Name]
- OSC Integration: Python `python-osc` library
- Visualization: Pygame library
- TouchDesigner: Derivative

---

## License

This project is part of THE LISTENER art installation (2025-2026).

For exhibition, research, and non-commercial use.

---

**Last Updated:** November 18, 2025
