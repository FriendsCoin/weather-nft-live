# THE LISTENER - Technical Documentation

Deep dive into the technical implementation of THE LISTENER.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1: ACCUMULATION                     │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Muse S     │      │ Preprocessing│      │   Feature    │
│  (4 ch EEG)  │─────▶│  (Filtering) │─────▶│  Extraction  │
│   256 Hz     │      │   Artifact   │      │ Band Powers  │
└──────────────┘      │   Removal    │      └──────────────┘
                      └──────────────┘             │
                                                   ▼
                                          ┌──────────────┐
                                          │     VAE      │
                                          │   Training   │
                                          │  (Learning)  │
                                          └──────────────┘
                                                   │
                                                   ▼
                                          ┌──────────────┐
                                          │   Latent     │
                                          │   Space      │
                                          │ (32-dim rep) │
                                          └──────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 PHASE 2: INTERPRETATION                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Sample     │      │    Claude    │      │   Stable     │
│   Latent     │─────▶│  (Interpret) │─────▶│  Diffusion   │
│   Space      │      │   Poetic     │      │   (Image)    │
└──────────────┘      │   Text       │      └──────────────┘
                      └──────────────┘             │
                                                   ▼
                                          ┌──────────────┐
                                          │   Visual     │
                                          │   Gallery    │
                                          │  (Memories)  │
                                          └──────────────┘
```

## Data Flow

### 1. EEG Acquisition

**Input:** Muse S headband (Bluetooth)

**Channels:**
- TP9 (left temporal)
- AF7 (left frontal)
- AF8 (right frontal)
- TP10 (right temporal)

**Sampling Rate:** 256 Hz

**Format:** CSV with columns `[timestamp, TP9, AF7, AF8, TP10]`

**Typical Values:** ±100 μV (microvolts)

### 2. Preprocessing Pipeline

**Purpose:** Clean signal, remove artifacts, normalize

**Steps:**

1. **Bandpass Filter (0.5-50 Hz)**
   - Remove DC offset and high-frequency noise
   - Keep EEG-relevant frequencies
   - Implementation: `scipy.signal.butter` or `mne.filter`

2. **Notch Filter (60 Hz)**
   - Remove powerline noise
   - 50 Hz for Europe, 60 Hz for US
   - Implementation: `scipy.signal.iirnotch`

3. **Artifact Removal**
   - Eye blinks: Large spikes in frontal channels (AF7, AF8)
   - Movement: Sudden amplitude changes
   - Methods:
     - Simple: Threshold-based removal + interpolation
     - Advanced: ICA (Independent Component Analysis)

4. **Normalization (Z-score)**
   - Mean = 0, Std = 1
   - Makes features comparable across sessions
   - Formula: `x_norm = (x - mean) / std`

**Output:** Clean EEG signals ready for feature extraction

### 3. Feature Extraction

**Purpose:** Convert raw EEG to meaningful meditation indicators

**Window-based Processing:**
- Window size: 4 seconds (1024 samples @ 256 Hz)
- Overlap: 50% (2 seconds step)
- Reason: Balance temporal resolution vs statistical stability

**Features per Window (34 total):**

#### A. Frequency Band Powers (20 features)

Using Welch's method (FFT-based power spectral density):

```python
frequencies, psd = scipy.signal.welch(signal, fs=256)
```

**Bands:**
- **Delta (0.5-4 Hz)**: Deep sleep, unconsciousness
- **Theta (4-8 Hz)**: 🧘 **Meditation**, drowsiness, REM sleep
- **Alpha (8-13 Hz)**: 🧘 **Relaxation**, eyes closed, calm focus
- **Beta (13-30 Hz)**: Active thinking, concentration, anxiety
- **Gamma (30-50 Hz)**: High-level cognition, binding

**Per channel:** 5 bands × 4 channels = **20 features**

**Interpretation for Meditation:**
- ↑ Alpha + ↑ Theta = Deep meditation
- ↑ Beta = Active mind, not settled
- ↓ Delta = Awake (not drowsy)

#### B. Hemispheric Asymmetry (2 features)

**Left Hemisphere:** TP9 + AF7
**Right Hemisphere:** TP10 + AF8

**Alpha Asymmetry:**
```
alpha_asym = log(alpha_right / alpha_left)
```

**Significance:**
- Positive (right > left): Approach state, positive affect
- Negative (left > right): Withdrawal state, contemplation

**Beta Asymmetry:** Same formula for beta band

#### C. Connectivity (6 features)

Pairwise Pearson correlations between channels:

```
TP9-AF7, TP9-AF8, TP9-TP10
AF7-AF8, AF7-TP10
AF8-TP10
```

**Interpretation:**
- High connectivity: Synchronized brain regions
- Low connectivity: Independent processing

#### D. Spectral Entropy (4 features)

Shannon entropy of power spectral density per channel:

```python
psd_norm = psd / psd.sum()
entropy = -sum(psd_norm * log(psd_norm))
```

**Interpretation:**
- Low entropy: Regular, rhythmic signal (deep meditation)
- High entropy: Complex, irregular signal (active mind)

#### E. Temporal Features (2 features)

- **Mean Absolute Derivative**: Signal smoothness
- **Spatial Variance**: Cross-channel variability

**Total:** 20 + 2 + 6 + 4 + 2 = **34 features**

### 4. VAE Model Architecture

**Type:** Variational Autoencoder (generative model)

**Why VAE, not classifier?**
- VAE learns DISTRIBUTION of meditation states
- Can generate "imagined" states (sampling)
- Captures continuous transitions, not discrete categories
- Unsupervised (no labels needed)

**Architecture:**

```
INPUT (34 features)
    ↓
ENCODER:
    Linear(34 → 128) + BatchNorm + ReLU + Dropout(0.2)
    Linear(128 → 64) + BatchNorm + ReLU + Dropout(0.2)
    Linear(64 → 32) + BatchNorm + ReLU + Dropout(0.2)
    ↓
LATENT SPACE (32-dimensional):
    μ (mean): Linear(32 → 32)
    log σ² (log variance): Linear(32 → 32)
    z ~ N(μ, σ²)  [Reparameterization trick]
    ↓
DECODER:
    Linear(32 → 32) + BatchNorm + ReLU + Dropout(0.2)
    Linear(32 → 64) + BatchNorm + ReLU + Dropout(0.2)
    Linear(64 → 128) + BatchNorm + ReLU + Dropout(0.2)
    Linear(128 → 34)
    ↓
OUTPUT (34 reconstructed features)
```

**Parameters:** ~35,000 trainable weights

**Loss Function:**

```
Total Loss = Reconstruction Loss + β × KL Divergence

Reconstruction = MSE(original, reconstructed)
KL Divergence = KL(q(z|x) || N(0,1))
```

**β-VAE:** β = 1.0 (standard VAE)
- Higher β: More regularized latent space, less reconstruction
- Lower β: Better reconstruction, less organized latent space

**Training Hyperparameters:**
- Optimizer: Adam (lr=0.001)
- Batch size: 32
- Epochs: 100 (with early stopping)
- Scheduler: ReduceLROnPlateau

**Checkpointing:**
- Save every 10 epochs
- Purpose: Track evolution of AI's understanding
- Files: `checkpoint_epoch_010.pt`, `checkpoint_epoch_020.pt`, etc.

### 5. Latent Space

**Dimension:** 32D continuous space

**Properties:**
- Each point represents a "meditation state"
- Smooth interpolation between states
- Organized by similarity (sessions cluster together)

**Operations:**

**A. Sampling (Random Generation):**
```python
z = torch.randn(n, 32)  # Sample from N(0, 1)
features = decoder(z)    # Generate features
```

**B. Reconstruction:**
```python
z = encoder(real_features)  # Encode real session
reconstructed = decoder(z)   # Reconstruct
```

**C. Interpolation:**
```python
z1 = encoder(state1)
z2 = encoder(state2)
z_mid = 0.5 * z1 + 0.5 * z2  # Midpoint
transition = decoder(z_mid)
```

### 6. LLM Interpretation

**Model:** Claude 3.5 Sonnet

**Temperature:** 0.8 (moderately creative)

**System Prompt:**
```
You are interpreting an AI companion's experience of witnessing
meditation through EEG data.

Generate SHORT poetic descriptions (2-3 sentences maximum).

Be contemplative and evocative, NOT clinical.
Avoid technical terms. Use phenomenological language.
Focus on: rhythm, depth, stillness, movement, transitions.
```

**Input to LLM:**
```
Sample features:
- Alpha rhythm: -1.234 (relaxation)
- Theta rhythm: -0.876 (deep meditation)
- Beta rhythm: -2.109 (mental activity)
- Hemispheric balance: -0.045
- Connectivity: 0.234
- Entropy: 1.567
```

**Output (Example):**
```
"Waves of stillness slowly dissolving into formless attention,
like breath disappearing into space. Occasional ripples of thought
quickly returning to stillness."
```

**Cost:** ~$0.005 per interpretation (very cheap!)

### 7. Image Generation

**Model:** Stable Diffusion XL (via Replicate API)

**Base Style:**
```
"contemplative abstract art, minimal, ethereal, soft colors"
```

**Negative Prompt:**
```
"text, words, letters, numbers, faces, people,
recognizable objects, photorealistic"
```

**Parameters:**
- Resolution: 768×768
- Inference steps: 50
- Guidance scale: 7.5

**Full Prompt Construction:**
```
"{llm_interpretation}, contemplative abstract art, minimal, ethereal"
```

**Example:**
```
Input: "Dense concentration crystallizing into sharp points"
Output: Abstract image with crystalline patterns in soft blues/purples
```

**Cost:** ~$0.02 per image

## Performance Considerations

### Training Speed

**CPU (MacBook Pro M1):**
- 10 sessions, 100 epochs: ~10 minutes
- 60 sessions, 100 epochs: ~30 minutes

**GPU (NVIDIA RTX 3080):**
- 10 sessions, 100 epochs: ~2 minutes
- 60 sessions, 100 epochs: ~8 minutes

### Memory Usage

**Training:**
- Model: ~140 MB
- Dataset (60 sessions): ~50 MB
- Total: ~200 MB
- Easily fits on any modern computer

### Storage

**Per Session (20-minute meditation):**
- Raw EEG CSV: ~15 MB
- Processed CSV: ~15 MB
- Features HDF5: ~1 MB
- Total per session: ~31 MB

**60 Sessions:** ~1.8 GB (manageable)

## Model Validation

### How to know it's working?

**1. Reconstruction Quality**
- Loss should decrease over epochs
- Val loss < 1.0 is good
- Reconstructed features should look similar to originals

**2. Latent Space Structure**
- UMAP visualization should show clusters
- Sessions should group together
- Smooth transitions between points

**3. Generated Samples**
- Should have realistic feature ranges
- Alpha/theta should be prominent (meditation)
- Not all zeros or all same values

**4. Interpretations**
- LLM output should be specific, not generic
- Different samples → different descriptions
- Descriptions should evolve across sessions

## Troubleshooting

### Model not learning (loss stuck)

**Causes:**
1. Too few sessions (need 10+)
2. Learning rate too high/low
3. Beta too high (over-regularization)

**Solutions:**
- Add more data
- Try lr=0.0001 or lr=0.01
- Reduce beta to 0.5

### Latent space collapsed

**Symptom:** All samples generate same output

**Cause:** KL divergence too weak, posterior collapse

**Solution:**
- Increase beta (try 2.0)
- Reduce latent dimension (try 16)
- Check for NaN in loss

### API costs too high

**Solutions:**
- Generate fewer samples initially
- Use `--skip-images` for testing
- Test with 5 samples before batch generation
- Claude API is very cheap (~$0.005/call)

## Extending THE LISTENER

### Add New Features

Edit `src/pipeline/feature_extraction.py`:

```python
def _extract_window_features(self, window):
    # ... existing features ...

    # Add your custom feature
    custom_feature = compute_something(window)
    features['my_custom_feature'] = custom_feature

    return features
```

### Change VAE Architecture

Edit `config.example.yaml`:

```yaml
model:
  latent_dim: 64  # Larger latent space
  encoder_layers: [256, 128, 64]  # Deeper network
  beta: 0.5  # Different regularization
```

### Customize LLM Prompts

Edit `src/utils/llm_interface.py` → `system_prompt`

### Add Real-time Visualization

Connect to TouchDesigner via OSC (Phase 3).

---

**For more details, see:**
- Code documentation (docstrings)
- `notebooks/` for interactive exploration
- `README.md` for conceptual overview
