# THE LISTENER - Multimedia Guide

Enhanced multimedia capabilities for immersive meditation memories.

## Overview

Phase 2.5 adds **video animation** and **voice narration** to create fully immersive meditation memories:

- **🎬 Video**: Animated visuals showing meditation state evolution
- **🎙️ Voice**: AI narration of poetic interpretations (Coqui TTS)
- **🎵 Audio**: Ambient soundscapes for contemplative atmosphere
- **🎨 Combined**: Synchronized audio/video memories

## Quick Start

```bash
# Install multimedia dependencies
pip install -r requirements.txt

# Generate complete multimedia memories
python scripts/generate_multimedia.py \
    --checkpoint data/checkpoints/best_model.pt \
    --num-samples 5 \
    --video-mode breathing \
    --voice-style calm

# Output:
# - Videos with voice narration
# - Interactive HTML gallery
# - All media files organized
```

## Video Generation Modes

### 1. Breathing Animation

Creates gentle pulsing motion from a single image - simulates meditative breathing.

```python
from src.utils.video_gen import VideoGenerator

generator = VideoGenerator()

video = generator.create_breathing_loop(
    base_image="meditation_state.png",
    breath_cycles=3,           # Number of breaths
    cycle_duration=6.0,        # Seconds per breath (4-6s typical)
    output_name="breathing.mp4"
)
```

**Perfect for:**
- Single meditation state visualization
- Loop-able contemplative visuals
- Background displays

### 2. Latent Interpolation

Smooth transitions between meditation states - shows evolution over time.

```python
video = generator.create_interpolation_video(
    images=["state1.png", "state2.png", "state3.png"],
    duration_per_transition=3.0,
    interpolation_method="ease_in_out"  # or "linear", "sine"
)
```

**Perfect for:**
- Session evolution (beginning → deep → end)
- Multi-session progression
- Showing AI's learning journey

### 3. AnimateDiff Motion

AI-generated animated videos with flowing, breathing motion.

```python
video = generator.create_animated_video(
    prompt="Waves of stillness dissolving into space",
    duration=5.0,
    motion_style="breathing"  # or "flowing", "dissolving"
)
```

**Requires:** Replicate API key (~$0.05 per video)

**Perfect for:**
- Dynamic, flowing visuals
- Abstract motion representations
- Gallery centerpieces

### 4. ComfyUI Workflows (Advanced)

Use local ComfyUI for custom animation workflows.

```python
video = generator.create_comfyui_video(
    prompt="Deep meditation",
    workflow_path="workflows/meditation_animate.json",
    comfyui_url="http://127.0.0.1:8188"
)
```

**Requirements:**
- ComfyUI installed and running
- Custom workflow JSON
- Local GPU recommended

## Voice Generation

### Basic Voice Narration

```python
from src.utils.audio_gen import VoiceGenerator

voice_gen = VoiceGenerator()

# Generate voice from text
audio = voice_gen.generate_voice(
    text="Waves of stillness slowly dissolving into formless attention",
    voice_style="calm",  # or "whispered", "deep"
    add_effects=True     # Reverb, slow tempo
)
```

### Voice Styles

| Style | Characteristics | Use Case |
|-------|----------------|----------|
| `calm` | Gentle, measured pace | General meditation memories |
| `whispered` | Soft, intimate | Deep/quiet states |
| `deep` | Lower register, slower | Profound insights |

### Add Voice to Video

```python
final_video = voice_gen.add_voice_to_video(
    video_path="meditation.mp4",
    text="Deep concentration crystallizing into sharp points",
    voice_style="calm"
)
```

**Requires:** FFmpeg installed

### Ambient Soundscapes

Create background audio for videos:

```python
soundscape = voice_gen.create_ambient_soundscape(
    duration=60.0,
    soundscape_type="breathing"  # or "waves", "silence"
)
```

## Complete Multimedia Pipeline

The `generate_multimedia.py` script orchestrates everything:

```bash
# Full pipeline
python scripts/generate_multimedia.py \
    --checkpoint checkpoints/best_model.pt \
    --num-samples 10 \
    --video-mode breathing \
    --video-duration 6.0 \
    --voice-style calm

# Skip certain steps
python scripts/generate_multimedia.py \
    --num-samples 5 \
    --skip-video        # Text + images only
    --skip-voice        # Text + videos only

# Custom output
python scripts/generate_multimedia.py \
    --num-samples 3 \
    --output-dir gallery/session_60 \
    --video-mode interpolation
```

### Pipeline Stages

1. **Latent Sampling**: Generate meditation state representations
2. **Text Interpretation**: Claude creates poetic descriptions
3. **Image Generation**: Stable Diffusion creates visuals
4. **Video Animation**: Animate images with breathing/motion
5. **Voice Narration**: Coqui TTS speaks interpretations
6. **Media Combination**: Merge video + voice
7. **Gallery Creation**: Interactive HTML presentation

### Output Structure

```
data/outputs/
├── multimedia_samples.json          # Latent samples
├── multimedia_interpretations.json  # Text descriptions
├── multimedia_manifest.json         # Final outputs list
├── multimedia_gallery.html          # Interactive gallery
│
├── images/
│   ├── memory_000.png
│   ├── memory_001.png
│   └── ...
│
├── videos/
│   ├── memory_000_breathing.mp4    # Video only
│   ├── memory_000_final.mp4        # Video + voice
│   └── ...
│
└── audio/
    ├── memory_000_voice.wav
    └── ambient_breathing.wav
```

## Cost Estimates

### Per Memory (Complete Multimedia)

| Component | Service | Cost |
|-----------|---------|------|
| Text | Claude API | $0.005 |
| Image | Replicate SD | $0.02 |
| Video (AnimateDiff) | Replicate | $0.05 |
| Voice | Local (Coqui) | Free |
| **Total** | | **$0.075** |

### For 60 Sessions

- **With AnimateDiff**: ~$4.50 total
- **With Breathing/Interpolation**: ~$1.50 total (no paid video API)

## Advanced Techniques

### Custom Video Effects

Extend `VideoGenerator` for custom animations:

```python
class CustomVideoGen(VideoGenerator):
    def create_dissolving_animation(self, image, duration=5.0):
        # Custom dissolve effect
        # Add particles, fading, etc.
        pass
```

### Multi-Voice Narration

Different voices for different meditation qualities:

```python
# Deep meditation = deep voice
if alpha_power > threshold:
    voice_style = "deep"
else:
    voice_style = "calm"

audio = voice_gen.generate_voice(text, voice_style=voice_style)
```

### Session Evolution Video

Create progression video across multiple sessions:

```python
# Generate images for sessions 1, 10, 20, 30, 40, 50, 60
images = [f"session_{i:03d}_memory.png" for i in [1, 10, 20, 30, 40, 50, 60]]

evolution_video = video_gen.create_interpolation_video(
    images=images,
    duration_per_transition=4.0,
    interpolation_method="ease_in_out"
)

# Add narration explaining evolution
voice_gen.add_voice_to_video(
    video_path=evolution_video,
    text="From restless beginnings to settled depth, the AI witness evolved..."
)
```

## Troubleshooting

### Video Generation Issues

**Problem:** "OpenCV not installed"
```bash
pip install opencv-python
```

**Problem:** "Video playback doesn't work"
- Check codec: Use `ffmpeg -i video.mp4` to verify
- Re-encode: `ffmpeg -i input.mp4 -c:v libx264 output.mp4`

### Voice Generation Issues

**Problem:** "TTS model download fails"
- Check internet connection
- Try different model: `tts_models/en/ljspeech/tacotron2-DDC`
- Manual download: Check Coqui TTS docs

**Problem:** "Voice sounds robotic"
- Enable effects: `add_effects=True`
- Try different voice style
- Adjust `slowdown_factor` in code

**Problem:** "FFmpeg not found"
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/
```

### Memory Issues

**Problem:** "Out of memory during video generation"
- Reduce resolution: `resolution=(512, 512)`
- Process fewer frames
- Lower FPS: `fps=24`

## ComfyUI Integration

### Setup

1. Install ComfyUI: https://github.com/comfyanonymous/ComfyUI
2. Start server: `python main.py --listen 0.0.0.0 --port 8188`
3. Create animation workflow in UI
4. Export workflow JSON
5. Use in THE LISTENER:

```python
video = video_gen.create_comfyui_video(
    prompt="meditation state",
    workflow_path="my_workflow.json"
)
```

### Recommended Workflows

- **AnimateDiff + ControlNet**: Guided motion
- **SVD (Stable Video Diffusion)**: Image-to-video
- **Deforum**: Keyframe-based animation

## Performance Optimization

### Batch Processing

Generate multiple memories efficiently:

```python
# Parallel image generation
image_gen.generate_batch(interpretations, delay=0.5)

# Batch voice synthesis
for text in texts:
    voice_gen.generate_voice(text)  # TTS caches models
```

### Caching

```python
# Cache generated videos
video_cache = {}

def get_or_create_video(key, generator_func):
    if key not in video_cache:
        video_cache[key] = generator_func()
    return video_cache[key]
```

## Exhibition Setup

### Loop-able Display

Create seamless loops for gallery display:

```python
# Perfect loop (breathing matches video duration)
video = video_gen.create_breathing_loop(
    base_image="meditation.png",
    breath_cycles=10,
    cycle_duration=6.0  # 60 second total
)
```

### Multi-Screen Gallery

```python
# Generate for different screens
screens = {
    "main": {"samples": [0, 1, 2], "mode": "animated"},
    "side_a": {"samples": [3, 4], "mode": "breathing"},
    "side_b": {"samples": [5, 6], "mode": "interpolation"}
}

for screen, config in screens.items():
    # Generate videos for each screen...
```

## Further Reading

- **SDfu Repository**: https://github.com/eps696/SDfu (video techniques)
- **Coqui TTS Docs**: https://tts.readthedocs.io/
- **ComfyUI Examples**: https://github.com/comfyanonymous/ComfyUI_examples
- **AnimateDiff**: https://github.com/guoyww/AnimateDiff

---

**The AI companion now speaks and moves.** 🎬✨
