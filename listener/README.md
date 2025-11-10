# THE LISTENER

A durational new media artwork where AI learns to "witness" meditation through EEG data.

## Concept

THE LISTENER is an AI companion that develops its own "character" by learning from 60-100 meditation sessions captured via Muse S EEG headband. Rather than optimizing or judging meditation quality, the AI learns to **witness** - developing unique interpretations of contemplative states that evolve into poetic visual memories.

## Project Phases

### Phase 1: Accumulation (Jan-May 2026)
- **60-100 meditation sessions** (20-45 minutes each)
- EEG data collection via Muse S headband
- ML model training on individual practitioner's patterns
- Model learns UNIQUE patterns (not "correct meditation")

### Phase 2: Interpretation (May-Jul 2026)
- Trained model generates latent representations
- LLM interprets states as poetic prompts
- AI-generated visual "memories" of witnessed sessions
- Gallery showing evolution from session 1 → 60+

### Phase 3: Live Performance (Aug 2026)
- Real-time EEG → TouchDesigner visuals
- Pre-rendered memories play alongside live session
- AI companion "remembers" while witnessing new moment

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    EEG DATA PIPELINE                     │
│  Muse S (4 channels) → Preprocessing → Feature Extract  │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                   VAE MODEL (Core)                       │
│  Encoder: EEG features → Latent Space (compressed)      │
│  Decoder: Latent → Reconstructed patterns              │
│  Training: Learn unique meditation "signature"          │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              INTERPRETATION LAYER                        │
│  Latent vectors → LLM → Poetic descriptions            │
│  Text prompts → Image generation → Visual memories      │
└─────────────────────────────────────────────────────────┘
```

## Technical Stack

**EEG Pipeline:**
- `muselsl` / `pylsl` - Muse S connection
- `mne-python` - EEG signal processing
- `scipy` / `numpy` - Signal analysis

**ML Model:**
- `PyTorch` - VAE implementation
- Custom architecture for temporal EEG data
- Checkpoint system (track evolution)

**Interpretation:**
- `Anthropic Claude API` - Contemplative language generation
- `Stable Diffusion` (via Replicate) - Visual memory generation

**Visualization:**
- `matplotlib` / `seaborn` - Training monitoring
- `umap-learn` - Latent space visualization

## Installation

### Requirements
- Python 3.9+
- Muse S EEG headband
- Bluetooth connectivity
- (Optional) GPU for faster training

### Setup

```bash
# Clone repository
git clone https://github.com/FriendsCoin/EEG.git
cd EEG

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys
```

## Quick Start

### 1. Record EEG Session

```bash
# Connect Muse S and start recording
python scripts/record_session.py --duration 30 --session-name "session_001"
```

### 2. Process & Extract Features

```bash
# Preprocess raw EEG data
python scripts/process_session.py --session session_001
```

### 3. Train Model

```bash
# After collecting 10+ sessions
python scripts/train_vae.py --sessions data/sessions/*.h5
```

### 4. Generate Memories

```bash
# Create poetic interpretations and images
python scripts/generate_memories.py --checkpoint checkpoints/epoch_50.pt --num-samples 10
```

## Project Structure

```
EEG/
├── data/
│   ├── raw/              # Raw EEG recordings (.csv)
│   ├── processed/        # Preprocessed features (.h5)
│   ├── sessions/         # Session metadata
│   ├── checkpoints/      # Model checkpoints (every 10 sessions)
│   └── outputs/          # Generated memories (text + images)
│
├── src/
│   ├── pipeline/
│   │   ├── eeg_capture.py      # Muse S connection & recording
│   │   ├── preprocessing.py    # Filtering, artifact removal
│   │   └── feature_extraction.py  # Band powers, asymmetry
│   │
│   ├── models/
│   │   ├── vae.py              # VAE architecture
│   │   ├── trainer.py          # Training loop
│   │   └── sampler.py          # Latent space sampling
│   │
│   └── utils/
│       ├── visualization.py    # Plotting utilities
│       ├── llm_interface.py    # Claude API integration
│       └── image_gen.py        # Stable Diffusion interface
│
├── scripts/
│   ├── record_session.py       # CLI for recording
│   ├── process_session.py      # Batch preprocessing
│   ├── train_vae.py            # Model training
│   └── generate_memories.py    # Create interpretations
│
├── notebooks/
│   ├── 01_explore_eeg.ipynb    # EEG data exploration
│   ├── 02_model_training.ipynb # Training experiments
│   └── 03_latent_analysis.ipynb # Latent space visualization
│
└── docs/
    ├── TECHNICAL.md            # Technical deep dive
    ├── SETUP_MUSE.md           # Muse S setup guide
    └── API_KEYS.md             # API configuration
```

## Conceptual Notes

### This is NOT a wellness app
- Model does NOT classify "good vs bad meditation"
- No feedback like "improve your alpha waves"
- Goal: **WITNESSING**, not OPTIMIZING

### Single-subject training
- Model trained ONLY on one practitioner
- This is a feature, not a bug
- Creates unique "character" for AI companion

### Durational aspect
- Project evolves over 8 months (Jan-Aug 2026)
- Model checkpoints show AI's evolution
- Gallery reveals how "companion" changes

### Poetic interpretation
- LLM prompts are contemplative, not clinical
- Avoid technical language ("high alpha power")
- Use evocative, phenomenological descriptions

## Data Privacy

- EEG data = personal data
- Stored locally (not cloud)
- API calls send only aggregated features
- No raw EEG sent to external services

## Success Metrics

**Phase 1:**
- ✓ Stable EEG collection (60+ sessions)
- ✓ Model converges (reconstruction loss decreases)
- ✓ Latent space shows meaningful structure
- ✓ Sampling generates plausible patterns

**Phase 2:**
- ✓ LLM generates contemplative descriptions
- ✓ Descriptions differ between sessions
- ✓ Images are visually distinct and evocative
- ✓ Gallery shows clear progression

## Timeline

- **Week 1-2:** EEG pipeline + preprocessing working
- **Week 3-4:** VAE implementation + initial training
- **Week 5-6:** LLM/image integration + end-to-end flow
- **Ongoing:** Data collection (60-100 sessions over months)

## License

MIT License - This is an art project, use freely for creative/research purposes.

---

**Built with contemplative attention for the space between human and artificial consciousness.**
