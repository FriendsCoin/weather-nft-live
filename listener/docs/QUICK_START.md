# THE LISTENER - Quick Start Guide

Get started with THE LISTENER in 15 minutes using mock data.

## Prerequisites

```bash
# Python 3.9+
python --version

# Clone repository
git clone https://github.com/FriendsCoin/EEG.git
cd EEG

# Install dependencies
pip install -r requirements.txt
```

## Option 1: Full Pipeline with Mock Data (Recommended for Testing)

Perfect for testing the entire system before connecting real EEG hardware.

### Step 1: Generate Mock Sessions (5 minutes)

```bash
# Generate 10 mock meditation sessions (30 seconds each for speed)
python scripts/generate_mock_data.py --num-sessions 10 --duration 30

# This creates:
# - data/raw/*.csv (raw EEG)
# - data/processed/*.csv (cleaned EEG)
# - data/sessions/*.h5 (extracted features)
```

You should see progress for each session:
```
Session 1/10
🎲 Generating mock EEG session...
📂 Loading session...
🔧 Applying filters...
✅ Session 1 complete!
```

### Step 2: Train the VAE (5-10 minutes)

```bash
# Train VAE on the generated sessions
python scripts/train.py --epochs 50 --batch-size 16

# On CPU: ~5-10 minutes for 50 epochs
# On GPU: ~2-3 minutes
```

Watch the training progress:
```
Epoch 1/50
   Train - Loss: 2.5432, Recon: 1.8765, KL: 0.6667
   Val   - Loss: 2.4981, Recon: 1.8234, KL: 0.6747
   💎 New best model saved
```

### Step 3: Generate Memories (2-5 minutes)

```bash
# Set API keys (get from https://console.anthropic.com and https://replicate.com)
export ANTHROPIC_API_KEY="your-key-here"
export REPLICATE_API_TOKEN="your-key-here"

# Generate 5 memories
python scripts/generate_memories.py --num-samples 5

# Skip images to test faster (text only):
python scripts/generate_memories.py --num-samples 5 --skip-images
```

Output:
```
[Step 1/3] Loading trained model...
[Step 2/3] Generating 5 samples from latent space...
[Step 3/3] Generating poetic interpretations...

1. "Waves of stillness slowly dissolving into formless attention,
    like breath disappearing into space."

2. "Dense concentration crystallizing into sharp points, then softening.
    The rhythm of effort and release."

[Step 4/4] Generating visual memories...
🖼️  Gallery created! Open: data/outputs/gallery.html
```

### Step 4: View Results

```bash
# Open gallery in browser
open data/outputs/gallery.html  # macOS
xdg-open data/outputs/gallery.html  # Linux
start data/outputs/gallery.html  # Windows

# Or view training progress
python scripts/visualize.py --history data/checkpoints/training_history.json
```

## Option 2: Real EEG with Muse S

For actual meditation practice tracking.

### Prerequisites

1. **Muse S headband** (charged and paired)
2. **muselsl installed**: `pip install muselsl`
3. **Bluetooth working** on your computer

### Step 1: Start Muse S Stream

In terminal 1:
```bash
# Connect to Muse S headband
muselsl stream --name "Muse-S"

# Should see:
# Looking for Muse device...
# Connected to Muse-S
# Streaming data...
```

Leave this running!

### Step 2: Record Session

In terminal 2:
```bash
# Record 20-minute session
python -m src.pipeline.eeg_capture --duration 1200 --session session_001

# Or using Python:
from src.pipeline.eeg_capture import MuseRecorder

recorder = MuseRecorder(output_dir="data/raw")
recorder.connect(timeout=30)
recorder.record(duration=1200, session_name="session_001")
```

### Step 3: Process Session

```bash
# Preprocess raw EEG
python -m src.pipeline.preprocessing \
    data/raw/session_001.csv \
    --output data/processed/session_001_clean.csv

# Extract features
python -m src.pipeline.feature_extraction \
    data/processed/session_001_clean.csv \
    --output data/sessions/session_001_features.h5
```

### Step 4: Collect More Sessions

Repeat steps 2-3 for **at least 10 sessions** (recommended: 60+).

The AI needs multiple sessions to learn your unique meditation pattern.

### Step 5: Train & Generate

Once you have 10+ sessions:

```bash
# Train VAE
python scripts/train.py --epochs 100

# Generate memories
python scripts/generate_memories.py --num-samples 20
```

## Common Issues

### "No EEG stream found"

**Problem:** Can't connect to Muse S

**Solutions:**
1. Check Muse S is charged and turned on
2. Pair Muse S with computer via Bluetooth settings first
3. Make sure `muselsl stream` is running in another terminal
4. Try: `muselsl list` to see available devices

### "No feature files found"

**Problem:** Training can't find data

**Solutions:**
1. Check files exist: `ls data/sessions/*.h5`
2. Generate mock data first: `python scripts/generate_mock_data.py`
3. Process sessions: See "Process Session" above

### "ANTHROPIC_API_KEY not set"

**Problem:** Can't generate interpretations

**Solutions:**
1. Get API key from https://console.anthropic.com/
2. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```
3. Or pass directly:
   ```bash
   python scripts/generate_memories.py --anthropic-key "sk-ant-..."
   ```

### "Replicate API error"

**Problem:** Can't generate images

**Solutions:**
1. Get API key from https://replicate.com/account
2. Set environment variable:
   ```bash
   export REPLICATE_API_TOKEN="r8_..."
   ```
3. Or skip images: `--skip-images` flag
4. Cost: ~$0.01-0.05 per image

### Training is very slow

**Solutions:**
1. Reduce epochs: `--epochs 50`
2. Reduce batch size: `--batch-size 16`
3. Use GPU if available (auto-detected)
4. For testing, use smaller dataset

## Next Steps

1. **Read Technical Documentation**: `docs/TECHNICAL.md`
2. **Explore Notebooks**: `notebooks/01_explore_eeg.ipynb`
3. **Customize**: Edit `config.example.yaml` and save as `config.yaml`
4. **Production**: Collect 60-100 real sessions over weeks/months

## Cost Estimate

**For 100 memories (typical art project scope):**
- Claude API: ~100 calls × $0.005 = **$0.50**
- Replicate (SD): ~100 images × $0.02 = **$2.00**
- **Total: ~$2.50**

Very affordable for an art project!

## Getting Help

- **Issues**: https://github.com/FriendsCoin/EEG/issues
- **Conceptual questions**: See `README.md` and `docs/TECHNICAL.md`
- **Muse S setup**: `docs/SETUP_MUSE.md`

---

**Happy witnessing!** 🧘‍♀️✨
