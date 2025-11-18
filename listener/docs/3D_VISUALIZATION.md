# 3D Visualization System

Interactive 3D visualizations for exploring meditation journeys, brain activity, and latent space evolution.

## Overview

THE LISTENER's 3D visualization system creates immersive, interactive visualizations that reveal patterns and evolution in your meditation practice. Perfect for personal exploration, scientific analysis, and exhibition displays.

**Features:**
- **3D Latent Space** - Journey through your meditation evolution in 3D space
- **3D Brain Activity** - Topographic visualization of EEG activity
- **Animated Journey** - Watch your progress unfold over time
- **VR Export** - Ready for Unity, Blender, or WebVR integration

## Quick Start

```bash
# Generate all 3D visualizations
python scripts/create_3d_viz.py --all

# Open in browser and explore!
```

This creates:
- `exports/3d/latent_space_3d_YYYYMMDD_HHMMSS.html` - Interactive 3D latent space
- `exports/3d/brain_activity_3d_session_XXX_YYYYMMDD_HHMMSS.html` - Brain topography
- `exports/3d/meditation_journey_YYYYMMDD_HHMMSS.html` - Animated evolution
- `exports/3d/vr_export_YYYYMMDD_HHMMSS/` - VR-ready data

---

## 1. 3D Latent Space Visualization

Explore your meditation sessions as points in 3D space, reduced from the 32-dimensional latent representation using UMAP, t-SNE, or PCA.

### What It Shows

- **Each point** = One meditation session
- **Position** = Similarity in brain states (close points = similar meditation)
- **Color** = Meditation depth, quality, or alpha performance
- **Size** = Signal quality or session duration
- **Trajectory line** = Chronological path through sessions

### Generation

```bash
# Basic latent space
python scripts/create_3d_viz.py --latent-space

# Use t-SNE instead of UMAP
python scripts/create_3d_viz.py --latent-space --method tsne

# Color by quality instead of depth
python scripts/create_3d_viz.py --latent-space --color-by quality

# Size by depth instead of quality
python scripts/create_3d_viz.py --latent-space --size-by depth

# Remove trajectory line
python scripts/create_3d_viz.py --latent-space --no-trajectory

# Last 30 days only
python scripts/create_3d_viz.py --latent-space --days 30
```

### Dimensionality Reduction Methods

| Method | Best For | Speed | Characteristics |
|--------|----------|-------|----------------|
| **UMAP** | General exploration | Medium | Preserves local + global structure |
| **t-SNE** | Finding clusters | Slow | Emphasizes local structure |
| **PCA** | Quick overview | Fast | Linear, preserves variance |

**Recommended**: UMAP (default) balances speed and quality.

### Color/Size Options

**Color by:**
- `depth` - Meditation depth (0-100) - shows progression to deeper states
- `quality` - Signal quality (0-100) - identifies good vs. noisy sessions
- `alpha_plus` - Alpha+ performance ratio - highlights focused states
- `date` - Chronological order - rainbow gradient over time

**Size by:**
- `quality` - Larger = better signal quality
- `depth` - Larger = deeper meditation
- `duration` - Larger = longer session

### Interaction

**In the browser:**
- **Drag** - Rotate view
- **Scroll** - Zoom in/out
- **Hover** - See session details (ID, depth, quality, date)
- **Click legend** - Hide/show trajectory

### Interpretation

**Clustering**: Sessions that are close together in 3D space had similar brain activity patterns, even if recorded at different times.

**Trajectory**: Follow the line to see your chronological journey. Loops indicate returning to similar states. Upward progression shows evolution to new patterns.

**Outliers**: Distant points represent unique meditation experiences - either exceptionally deep, or unusually distracted.

**Example insights:**
- "Sessions from morning vs. evening form distinct clusters"
- "My meditation has evolved from scattered points to a focused cluster"
- "After 2 weeks of practice, I reached a new region of state space"

---

## 2. 3D Brain Activity Topography

Visualize EEG activity as a 3D topographic map on a head model, showing spatial distribution of brain waves.

### What It Shows

- **3D head sphere** - Wireframe representing your head
- **Electrode markers** - AF7, AF8, TP9, TP10 positions (Muse S channels)
- **Color surface** - Interpolated power distribution across scalp
- **Marker size** - Activity level at each electrode

### Generation

```bash
# Most recent session
python scripts/create_3d_viz.py --brain-activity

# Specific session
python scripts/create_3d_viz.py --brain-activity --session session_001
```

### Interaction

- **Drag** - Rotate head to view from different angles
- **Zoom** - See electrode details
- **Hover** - View exact power values

### Interpretation

**Hot colors (red/yellow)**: High activity regions - often frontal during focused meditation, temporal during relaxed states.

**Cool colors (blue/purple)**: Low activity - typically indicates calmness or reduced mental chatter.

**Frontal dominance (AF7/AF8 hot)**: Active thinking, focus, or concentration.

**Temporal dominance (TP9/TP10 hot)**: Creative states, relaxation, or drowsiness.

**Balanced activity**: Ideal meditation state - moderate activity across all regions.

---

## 3. Meditation Journey Animation

Watch your meditation practice evolve over time with an interactive animation showing the cumulative trajectory through latent space.

### What It Shows

- **Progressive revelation** - Sessions appear one by one
- **Trajectory growth** - Line extends as practice deepens
- **Depth evolution** - Color changes show depth progression
- **Time slider** - Scrub through your entire journey

### Generation

```bash
# Full journey
python scripts/create_3d_viz.py --journey

# Last 60 days
python scripts/create_3d_viz.py --journey --days 60

# Use PCA for faster rendering
python scripts/create_3d_viz.py --journey --method pca
```

### Interaction

- **Play** - Automatically advance through sessions
- **Slider** - Manually scrub to any point in time
- **Pause** - Freeze at interesting moments
- **Rotate** - View trajectory from any angle

### Interpretation

**Early sessions**: Often scattered, exploring different states.

**Mid-practice**: Trajectory may loop as you find favorite states and return to them.

**Advanced practice**: Trajectory often ventures into new territories (deeper states, novel patterns).

**Plateaus**: Horizontal segments indicate consistent states over multiple sessions.

**Breakthroughs**: Sudden jumps to new regions indicate significant shifts in practice.

---

## 4. VR Export

Export your meditation data for use in VR environments (Unity, Unreal, A-Frame) or 3D software (Blender, Maya).

### What's Exported

```
vr_export_YYYYMMDD_HHMMSS/
  ├── vr_meditation_space.json    # Session positions and metadata
  ├── session_000.obj              # 3D sphere mesh (session 1)
  ├── session_001.obj              # 3D sphere mesh (session 2)
  └── ...                          # One OBJ per session
```

### Generation

```bash
# Export for VR
python scripts/create_3d_viz.py --vr-export

# Last 30 days for faster loading in VR
python scripts/create_3d_viz.py --vr-export --days 30
```

### JSON Format

```json
{
  "method": "umap",
  "n_sessions": 50,
  "positions": [
    [x1, y1, z1],
    [x2, y2, z2],
    ...
  ],
  "sessions": [
    {
      "session_id": "session_001",
      "depth": 75.3,
      "quality": 92.1,
      "date": "2025-01-15"
    },
    ...
  ]
}
```

### Unity Integration

```csharp
// C# script for Unity
using UnityEngine;
using System.IO;

[System.Serializable]
public class MeditationData {
    public string method;
    public int n_sessions;
    public float[][] positions;
    public SessionData[] sessions;
}

[System.Serializable]
public class SessionData {
    public string session_id;
    public float depth;
    public float quality;
    public string date;
}

public class MeditationVR : MonoBehaviour {
    void Start() {
        // Load JSON
        string json = File.ReadAllText("vr_meditation_space.json");
        MeditationData data = JsonUtility.FromJson<MeditationData>(json);

        // Create sphere for each session
        for (int i = 0; i < data.n_sessions; i++) {
            Vector3 pos = new Vector3(
                data.positions[i][0],
                data.positions[i][1],
                data.positions[i][2]
            );

            GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            sphere.transform.position = pos;

            // Color by depth
            float depth = data.sessions[i].depth / 100f;
            Color color = Color.Lerp(Color.blue, Color.magenta, depth);
            sphere.GetComponent<Renderer>().material.color = color;
        }
    }
}
```

### Blender Integration

1. **Import OBJ meshes:**
   - File → Import → Wavefront (.obj)
   - Select all `session_*.obj` files
   - They'll appear at correct 3D positions

2. **Color by depth using Python:**
   ```python
   import bpy
   import json

   # Load JSON
   with open('vr_meditation_space.json') as f:
       data = json.load(f)

   # Color each object
   for i, obj in enumerate(bpy.data.objects):
       if obj.name.startswith('session_'):
           depth = data['sessions'][i]['depth'] / 100.0
           mat = bpy.data.materials.new(name=f"Session_{i}")
           mat.diffuse_color = (depth, 0.3, 1.0-depth, 1.0)  # Blue to pink
           obj.data.materials.append(mat)
   ```

3. **Render beautiful stills for exhibition**

### A-Frame WebVR

```html
<!-- WebVR meditation space -->
<html>
  <head>
    <script src="https://aframe.io/releases/1.4.0/aframe.min.js"></script>
  </head>
  <body>
    <a-scene>
      <a-sky color="#0a0e27"></a-scene>

      <!-- Load via JavaScript -->
      <script>
        fetch('vr_meditation_space.json')
          .then(r => r.json())
          .then(data => {
            const scene = document.querySelector('a-scene');

            data.positions.forEach((pos, i) => {
              const sphere = document.createElement('a-sphere');
              sphere.setAttribute('position', `${pos[0]} ${pos[1]} ${pos[2]}`);
              sphere.setAttribute('radius', '0.1');

              const depth = data.sessions[i].depth / 100;
              const color = `hsl(${250 + depth * 50}, 80%, 60%)`;
              sphere.setAttribute('color', color);

              scene.appendChild(sphere);
            });
          });
      </script>
    </a-scene>
  </body>
</html>
```

---

## Advanced Usage

### Filtering Sessions

```bash
# Only deep sessions (depth > 70)
python scripts/create_3d_viz.py --all --min-depth 70

# Only high quality (quality > 80)
python scripts/create_3d_viz.py --all --min-quality 80

# Last 7 days, depth > 50
python scripts/create_3d_viz.py --all --days 7 --min-depth 50
```

### Comparing Time Periods

```bash
# First 30 days
python scripts/create_3d_viz.py --latent-space --days 30 --output-dir exports/3d/early

# Last 30 days
python scripts/create_3d_viz.py --latent-space --days 30 --output-dir exports/3d/recent

# Open both in browser and compare!
```

### Custom Themes

```bash
# Light theme for presentations
python scripts/create_3d_viz.py --all --theme light

# Dark theme for exhibition (default)
python scripts/create_3d_viz.py --all --theme dark
```

### Batch Processing

```bash
# Generate weekly visualizations
for weeks in 1 2 3 4; do
    python scripts/create_3d_viz.py --latent-space \
        --days $((weeks * 7)) \
        --output-dir exports/3d/week_$weeks
done
```

---

## Interpretation Guide

### Reading Latent Space

**Question**: "Why are my sessions clustered?"

**Answer**: Sessions with similar brain activity patterns will cluster together. This is good! It means you're consistently reaching similar meditation states.

**Question**: "What do outliers mean?"

**Answer**: Outliers represent unique sessions - either breakthroughs to deep states, or unusually distracted sessions. Check the depth/quality to distinguish.

**Question**: "My trajectory makes loops - is that bad?"

**Answer**: No! Loops mean you're returning to familiar states, which shows you're developing a stable practice. Linear trajectories without loops might indicate you're still exploring.

### Brain Activity Patterns

**Frontal hot (AF7/AF8)**: Active concentration. Common in early meditation or when dealing with thoughts.

**Temporal hot (TP9/TP10)**: Relaxed awareness. Common in deep meditation or creative states.

**Balanced**: Even distribution suggests integrated awareness - a desirable state.

**Left-right asymmetry**: Normal! Everyone has slightly different hemispheric activation.

### Journey Animations

**Smooth progression**: Gradual skill development over time.

**Sudden jumps**: Breakthrough moments (new technique, insight, or external change).

**Plateaus**: Consolidation periods - practice is stable, not necessarily stagnant.

**Return to origin**: Revisiting beginner states can happen during stress or illness.

---

## Exhibition Setup

### Large Display Installation

**Hardware:**
- 4K display or projector
- Computer with GPU (for smooth rotation)
- Mouse/trackpad for interaction

**Software:**
1. Generate visualizations with `--theme dark`
2. Open in Chrome/Firefox (best 3D performance)
3. Full screen (F11)
4. Pre-rotate to interesting angle
5. Leave hover info visible for audience

**Interaction:**
- Visitors can rotate and explore
- Provide instructions: "Drag to rotate, scroll to zoom"
- Consider tablet with orientation lock for easier control

### VR Gallery

**Platforms:**
- **Oculus Quest**: Use A-Frame WebVR approach
- **SteamVR**: Use Unity integration
- **Google Cardboard**: Mobile WebVR

**Experience design:**
1. Spawn user in center of meditation space
2. Each session appears as a glowing sphere
3. Point at sphere to see session details
4. Trajectory line connects sessions chronologically
5. Audio: Ambient meditation sounds, subtle chimes when deep sessions are viewed

### Video Loops for Silent Display

Use screen recording to capture rotation:

```bash
# 1. Open visualization in browser
# 2. Start screen recording
# 3. Slowly rotate 360° over 60 seconds
# 4. Export as MP4
# 5. Loop in exhibition

# Or use headless Chrome for automation:
chromium --headless --screenshot=viz.png latent_space_3d.html
```

---

## Troubleshooting

### "Not enough sessions"

**Error**: `Need at least 2 sessions with latent vectors`

**Solution**: Train more meditation sessions. UMAP/t-SNE need minimum 2 points, but 10+ is better for meaningful visualization.

### "Dimensionality reduction takes too long"

**Problem**: t-SNE is slow with 100+ sessions

**Solution**:
- Use UMAP (faster): `--method umap`
- Or PCA (fastest): `--method pca`
- Or filter recent sessions: `--days 60`

### "Points all overlap"

**Problem**: All sessions look the same in 3D space

**Solution**: This means your sessions are very similar (good for consistency!). Try:
- Increase min_dist: Edit `visualization_3d.py`, increase `min_dist` to 0.3
- Use t-SNE: `--method tsne` (emphasizes small differences)
- Color by quality to see which overlapping points are high-quality

### "VR export crashes Unity"

**Problem**: Too many meshes

**Solution**:
- Filter sessions: `--vr-export --days 30`
- Or use instanced rendering in Unity
- Or merge meshes in Blender before import

### "Plotly visualization won't load"

**Problem**: HTML file too large

**Solution**:
- Reduce data: `--days 30`
- Or split into multiple visualizations
- Or reduce n_neighbors (faster, smaller): Edit code, set `n_neighbors=5`

---

## Performance Tips

### For Many Sessions (100+)

```bash
# Use UMAP (faster than t-SNE)
python scripts/create_3d_viz.py --all --method umap

# Or PCA (fastest)
python scripts/create_3d_viz.py --all --method pca

# Or split time periods
python scripts/create_3d_viz.py --latent-space --days 30  # Last month
python scripts/create_3d_viz.py --latent-space --days 90  # Last quarter
```

### For Exhibition (Smooth Interaction)

- Use Chrome or Firefox (best WebGL performance)
- Close other tabs
- Reduce particle count: Edit `visualization_3d.py`, reduce grid resolution
- Pre-load before exhibition starts

---

## Scientific Applications

### Research Questions

**1. Does meditation depth improve over time?**
- Generate journey animation
- Watch color progression (depth)
- Quantify: Measure average z-coordinate change

**2. Do meditation states cluster by technique?**
- Color by technique (add metadata)
- Visualize: Do different techniques occupy different regions?

**3. Is there a relationship between quality and depth?**
- Create latent space: `--color-by depth --size-by quality`
- Observe: Are large (high quality) points also dark (high depth)?

### Data Export for Stats

The VR export JSON can be used for statistical analysis:

```python
import json
import numpy as np
from scipy.stats import spearmanr

# Load positions
with open('vr_export/vr_meditation_space.json') as f:
    data = json.load(f)

positions = np.array(data['positions'])
depths = [s['depth'] for s in data['sessions']]

# Correlation between z-coordinate and depth
corr, p = spearmanr(positions[:, 2], depths)
print(f"Z-depth correlation: r={corr:.3f}, p={p:.3f}")

# Are deeper sessions further from origin?
distances = np.linalg.norm(positions, axis=1)
corr, p = spearmanr(distances, depths)
print(f"Distance-depth correlation: r={corr:.3f}, p={p:.3f}")
```

---

## Future Enhancements

Planned features (contributions welcome!):

- [ ] **Animated camera paths** - Pre-defined tours through meditation space
- [ ] **Cluster detection** - Automatic identification of meditation state clusters
- [ ] **Temporal coloring** - Gradient color schemes showing time progression
- [ ] **Multi-user spaces** - Compare meditation journeys between practitioners
- [ ] **Sound mapping** - Generate audio based on position in latent space
- [ ] **VR interaction** - Grab and examine sessions in VR
- [ ] **Time-lapse videos** - Automated screen recording of journey evolution

---

## Resources

### Dimensionality Reduction
- UMAP: https://umap-learn.readthedocs.io/
- t-SNE: https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
- PCA: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html

### 3D Visualization
- Plotly: https://plotly.com/python/3d-charts/
- WebGL: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API

### VR Development
- A-Frame: https://aframe.io/
- Unity: https://unity.com/
- Three.js: https://threejs.org/

### EEG Topography
- MNE-Python: https://mne.tools/stable/auto_tutorials/evoked/20_visualize_evoked.html

---

## Credits

**THE LISTENER** - AI Meditation Companion
- 3D Visualization: Plotly, UMAP, SciPy
- VR Export: OBJ mesh format
- Interactive Exploration: WebGL

---

## License

This project is part of THE LISTENER art installation (2025-2026).

For exhibition, research, and non-commercial use.

---

**Last Updated:** November 18, 2025
