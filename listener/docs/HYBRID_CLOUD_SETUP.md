# Hybrid Local + Cloud Setup for THE LISTENER

**Use Case:** Capture EEG locally, process heavy tasks on cloud GPUs (vast.ai, Runpod, Lambda Labs, etc.)

**Best For:**
- Local EEG capture with Muse S headband
- Cloud GPU training and image/video generation
- Cost-effective: Only pay for GPU when needed
- More powerful GPUs than RTX 2080 (e.g., RTX 4090, A100)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Cloud Provider Options](#cloud-provider-options)
3. [vast.ai Setup Guide](#vastai-setup-guide)
4. [Data Synchronization](#data-synchronization)
5. [Remote Workflows](#remote-workflows)
6. [Cost Optimization](#cost-optimization)
7. [Example Workflows](#example-workflows)

---

## Architecture Overview

### Division of Labor

**🏠 LOCAL MACHINE (Your Windows/WSL):**
- ✅ EEG data capture (Muse S headband)
- ✅ Preprocessing (MNE-Python, CPU-based)
- ✅ Feature extraction (CPU-based)
- ✅ Data storage and organization
- ✅ Meditation analysis (CPU-based)
- ✅ Project management and code editing

**☁️ CLOUD GPU (vast.ai, etc.):**
- ✅ VAE model training (GPU-intensive)
- ✅ Stable Diffusion image generation (GPU-intensive)
- ✅ AnimateDiff video generation (GPU-intensive)
- ✅ Large batch processing
- ✅ Experimentation with different models

### Data Flow

```
┌─────────────────┐
│  Muse S Headset │
└────────┬────────┘
         │ EEG data
         ▼
┌─────────────────┐
│ LOCAL: Capture  │  ← You are here (Windows/WSL)
│ & Preprocessing │
└────────┬────────┘
         │ Features (.h5)
         │
    ┌────┴────┐
    │  rsync/ │  ← Sync data to cloud
    │  git    │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│ CLOUD: Training │  ← vast.ai GPU instance
│ & Generation    │
└────────┬────────┘
         │ Outputs (images, videos, checkpoints)
         │
    ┌────┴────┐
    │  rsync  │  ← Sync results back
    └────┬────┘
         │
         ▼
┌─────────────────┐
│ LOCAL: Analysis │  ← Review and curate
│ & Curation      │
└─────────────────┘
```

---

## Cloud Provider Options

### 1. **vast.ai** (Recommended for Budget)

**Pros:**
- ✅ Cheapest option (~$0.20-0.80/hr for RTX 3090/4090)
- ✅ Spot pricing available
- ✅ Wide GPU selection
- ✅ Easy to use

**Cons:**
- ⚠️ Community cloud (variable reliability)
- ⚠️ Machines can be interrupted
- ⚠️ Network speeds vary

**Best For:** Experimentation, training, batch processing

**Pricing Examples:**
- RTX 3090 (24GB): ~$0.30/hr
- RTX 4090 (24GB): ~$0.60/hr
- A100 (40GB): ~$1.20/hr

### 2. **RunPod**

**Pros:**
- ✅ More reliable than vast.ai
- ✅ Good network speeds
- ✅ Persistent storage available
- ✅ Jupyter notebooks built-in

**Cons:**
- ⚠️ Slightly more expensive (~$0.40-1.00/hr)

**Pricing Examples:**
- RTX 3090: ~$0.44/hr
- RTX 4090: ~$0.79/hr
- A100: ~$1.89/hr

### 3. **Lambda Labs**

**Pros:**
- ✅ Professional-grade
- ✅ Very fast network
- ✅ Persistent storage included
- ✅ Excellent uptime

**Cons:**
- ⚠️ More expensive (~$0.50-2.00/hr)
- ⚠️ Less GPU selection

### 4. **Google Colab Pro+**

**Pros:**
- ✅ Simple setup (Jupyter in browser)
- ✅ Fixed price ($50/month)
- ✅ Good for experimentation

**Cons:**
- ⚠️ Session limits (12-24 hours)
- ⚠️ Less control over environment
- ⚠️ A100 not always available

---

## vast.ai Setup Guide

### Step 1: Create Account

1. Go to https://vast.ai
2. Sign up and add payment method
3. Load $10-20 credit (good for ~20-40 hours of RTX 3090)

### Step 2: Choose GPU Instance

**For THE LISTENER, recommended specs:**

```
GPU:          RTX 3090 or RTX 4090 (24GB VRAM)
CPU:          4+ cores
RAM:          16GB+ system RAM
Disk:         50GB+ SSD (for models and data)
Network:      100+ Mbps upload (for syncing results)
Cost target:  $0.30-0.60/hr
```

**Search Filters:**
```
GPU: RTX 3090 or RTX 4090
VRAM: >= 24 GB
Disk: >= 50 GB
Verified: Yes (more reliable)
Sort by: $/hr (cheapest first)
```

### Step 3: Launch Instance

**Template Selection:**
- **Option 1:** PyTorch template (recommended)
- **Option 2:** Custom template (more control)

**Launch Command:**
```bash
# Use PyTorch template with Jupyter
# It includes: PyTorch, CUDA, Jupyter, SSH access
```

### Step 4: Connect via SSH

**Get SSH command from vast.ai dashboard:**
```bash
ssh -p 12345 root@123.456.789.0 -L 8080:localhost:8080
```

**Better: Add to ~/.ssh/config**
```
Host vast-listener
    HostName 123.456.789.0
    Port 12345
    User root
    LocalForward 8080 localhost:8080
    ServerAliveInterval 60
```

**Then connect:**
```bash
ssh vast-listener
```

### Step 5: Setup Environment

**On the cloud GPU:**

```bash
# Clone the project
git clone https://github.com/FriendsCoin/weather-nft-live.git
cd weather-nft-live/listener

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-local-gpu.txt

# Verify GPU
nvidia-smi
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Test setup
python scripts/test_gpu_setup.py
```

---

## Data Synchronization

### Strategy 1: rsync (Recommended for Large Files)

**Upload data TO cloud:**
```bash
# From your local machine
rsync -avz --progress \
    data/sessions/ \
    vast-listener:~/weather-nft-live/listener/data/sessions/

# Or specific session
rsync -avz --progress \
    data/sessions/session_*.h5 \
    vast-listener:~/weather-nft-live/listener/data/sessions/
```

**Download results FROM cloud:**
```bash
# Download trained models
rsync -avz --progress \
    vast-listener:~/weather-nft-live/listener/outputs/checkpoints/ \
    ./outputs/checkpoints/

# Download generated images
rsync -avz --progress \
    vast-listener:~/weather-nft-live/listener/outputs/images/ \
    ./outputs/images/

# Download videos
rsync -avz --progress \
    vast-listener:~/weather-nft-live/listener/outputs/videos/ \
    ./outputs/videos/
```

### Strategy 2: Git (Code Sync)

**On local machine:**
```bash
# Commit your local changes
git add .
git commit -m "Update session data"
git push
```

**On cloud GPU:**
```bash
# Pull latest code
git pull

# Note: Don't commit data files to git!
# Use .gitignore for data/
```

### Strategy 3: Cloud Storage (Alternative)

**Option A: Google Drive (rclone)**
```bash
# Install rclone on cloud GPU
curl https://rclone.org/install.sh | sudo bash

# Configure Google Drive
rclone config

# Upload outputs to Google Drive
rclone sync outputs/ gdrive:listener-outputs/
```

**Option B: AWS S3 / Wasabi**
```bash
# Install AWS CLI
pip install awscli

# Upload to S3
aws s3 sync outputs/ s3://my-listener-bucket/outputs/
```

---

## Remote Workflows

### Workflow 1: Remote Training

**Local → Cloud → Local**

**On local (Windows/WSL):**
```bash
# 1. Capture and process sessions locally
python scripts/capture_session.py --duration 300 --output session_001
python scripts/extract_features.py --session session_001.csv

# 2. Upload to cloud
rsync -avz data/sessions/session_*.h5 vast-listener:~/listener/data/sessions/
```

**On cloud GPU (SSH):**
```bash
# 3. Train VAE on powerful GPU
cd ~/listener
python scripts/train.py \
    --data data/sessions \
    --epochs 100 \
    --batch-size 64 \
    --output outputs/checkpoints/model_v1.pt

# Training runs much faster on RTX 4090!
# RTX 2080:  ~5s/epoch
# RTX 4090:  ~1s/epoch (5x faster!)
```

**On local:**
```bash
# 4. Download trained model
rsync -avz vast-listener:~/listener/outputs/checkpoints/ ./outputs/checkpoints/

# 5. Use locally for analysis
python scripts/analyze_meditation.py --checkpoint outputs/checkpoints/model_v1.pt
```

### Workflow 2: Remote Image Generation

**On cloud GPU:**
```bash
# Generate meditation memories on powerful GPU
python scripts/generate_multimedia.py \
    --checkpoint outputs/checkpoints/best_model.pt \
    --num-samples 60 \
    --use-local-gpu \
    --config configs/lowmem_gpu.yaml \
    --video-mode animatediff \
    --add-voice

# Much faster on RTX 4090:
# - SD image: ~2s (vs 4.5s on RTX 2080)
# - AnimateDiff: ~15s (vs 45s on RTX 2080)
# - 60 samples: ~30 minutes (vs 2+ hours local)
```

**Download results:**
```bash
rsync -avz vast-listener:~/listener/outputs/ ./outputs/
```

### Workflow 3: Remote Jupyter Notebook

**On cloud GPU:**
```bash
# Start Jupyter (vast.ai templates include this)
jupyter lab --ip 0.0.0.0 --port 8080 --no-browser --allow-root
```

**On local:**
```
# SSH tunnel is already set up (LocalForward 8080)
# Open browser: http://localhost:8080
```

**Now you can:**
- Run interactive analysis
- Test models in real-time
- Visualize results
- Debug code

### Workflow 4: VSCode Remote SSH

**On local (VSCode):**
```
1. Install "Remote - SSH" extension
2. Cmd+Shift+P → "Remote-SSH: Connect to Host"
3. Select "vast-listener"
4. VSCode opens connected to cloud GPU!
```

**Now you can:**
- Edit code on cloud GPU directly
- Run terminals on cloud GPU
- Debug with full IDE features
- See GPU usage in real-time

---

## Cost Optimization

### Tips to Save Money

**1. Use Spot Instances (vast.ai)**
- ✅ 50-70% cheaper
- ⚠️ Can be interrupted
- ✅ Good for: Training (use checkpoints), batch processing
- ❌ Bad for: Long interactive sessions

**2. Shutdown When Not Needed**
```bash
# After training completes, sync and destroy
rsync -avz outputs/ local-machine:~/outputs/
# Then destroy instance on vast.ai dashboard
```

**3. Use Smaller GPUs for Testing**
```
RTX 3060 (12GB): ~$0.15/hr  ← Test code here first
RTX 3090 (24GB): ~$0.30/hr  ← Production runs
RTX 4090 (24GB): ~$0.60/hr  ← Fast production
```

**4. Batch Your Work**
```
Instead of:
  - Start instance → Train 1 session → Stop ($0.30)
  - Start instance → Train 1 session → Stop ($0.30)
  × 10 sessions = $3.00

Do this:
  - Start instance → Train 10 sessions → Stop ($0.30 × 1 hour)
  = $0.30 (10x cheaper!)
```

**5. Use Local for Light Tasks**
```
Local (free):
  - Data capture
  - Preprocessing
  - Feature extraction
  - Analysis
  - Meditation metrics

Cloud (paid):
  - VAE training
  - Image generation
  - Video generation
```

### Cost Estimates

**60-Session Project (8 months):**

| Task | Local | vast.ai RTX 3090 | Savings |
|------|-------|------------------|---------|
| Data capture | Free | N/A | N/A |
| Preprocessing | Free | ~$0.50 | $0.50 |
| VAE training | ~2 hours | ~20 min | 6x faster |
| | (Free) | $0.10 | $0 saved |
| Image gen (60) | ~4 hours | ~40 min | 6x faster |
| | (Free) | $0.20 | $0 saved |
| Video gen (60) | ~1 hour | ~15 min | 4x faster |
| | (Free) | $0.08 | $0 saved |
| **Total** | **Free** | **~$0.88** | Time saved! |

**Alternative: Full Cloud (Replicate API):**
- Cost: ~$1.50 for 60 sessions
- Cloud GPU is actually cheaper if you batch!

**Hybrid Recommendation:**
- Capture locally (must be local for Muse S)
- Process locally (free, good enough)
- Train on cloud if >100 sessions or experimenting
- Generate images/videos on cloud if speed matters

---

## Example Workflows

### Example 1: Weekly Meditation Session Processing

**Sunday: Capture Week's Sessions**
```bash
# On local machine
for i in {1..7}; do
    python scripts/capture_session.py --duration 600 --output session_$i
    python scripts/extract_features.py --session session_$i.csv
done
```

**Monday: Cloud Processing**
```bash
# Start vast.ai instance (RTX 3090)

# Upload week's data
rsync -avz data/sessions/ vast-listener:~/listener/data/sessions/

# SSH to cloud
ssh vast-listener

# Train VAE on all accumulated sessions
python scripts/train.py --data data/sessions --epochs 50

# Generate memories for this week
python scripts/generate_multimedia.py --num-samples 7 --use-local-gpu

# Exit and download results
exit

# Download on local
rsync -avz vast-listener:~/listener/outputs/ ./outputs/

# Destroy vast.ai instance (save money!)
```

**Total time on cloud: ~30 minutes = ~$0.15**

### Example 2: Model Experimentation

**Scenario:** Test 3 different VAE architectures

**On cloud:**
```bash
# Experiment 1: Standard VAE (32D latent)
python scripts/train.py --latent-dim 32 --output model_32d.pt

# Experiment 2: Large VAE (64D latent)
python scripts/train.py --latent-dim 64 --output model_64d.pt

# Experiment 3: Small VAE (16D latent)
python scripts/train.py --latent-dim 16 --output model_16d.pt

# Compare results
python scripts/compare_models.py model_*.pt
```

**Total time: ~1 hour = ~$0.30**

**On local (would take 5+ hours):**
- Not practical for experimentation

### Example 3: Final Art Piece Generation

**Scenario:** Generate 100 high-quality meditation memories for exhibition

**On cloud (RTX 4090):**
```bash
python scripts/generate_multimedia.py \
    --checkpoint best_model.pt \
    --num-samples 100 \
    --use-local-gpu \
    --video-mode animatediff \
    --add-voice \
    --high-quality

# RTX 4090: ~50 minutes
# Cost: ~$0.50
```

**On local (RTX 2080):**
```bash
# Same command
# RTX 2080: ~3-4 hours
# Cost: Free electricity, but much slower
```

---

## Helper Scripts

### Script 1: Sync to Cloud

**`scripts/sync_to_cloud.sh`:**
```bash
#!/bin/bash
# Sync local data to cloud GPU

CLOUD_HOST="vast-listener"
LOCAL_DIR="data/sessions"
REMOTE_DIR="~/weather-nft-live/listener/data/sessions"

echo "Syncing $LOCAL_DIR to $CLOUD_HOST..."
rsync -avz --progress \
    --exclude='*.tmp' \
    --exclude='__pycache__' \
    $LOCAL_DIR/ \
    $CLOUD_HOST:$REMOTE_DIR/

echo "✓ Sync complete!"
```

### Script 2: Sync from Cloud

**`scripts/sync_from_cloud.sh`:**
```bash
#!/bin/bash
# Download results from cloud GPU

CLOUD_HOST="vast-listener"
REMOTE_DIR="~/weather-nft-live/listener/outputs"
LOCAL_DIR="outputs"

echo "Downloading outputs from $CLOUD_HOST..."
rsync -avz --progress \
    $CLOUD_HOST:$REMOTE_DIR/ \
    $LOCAL_DIR/

echo "✓ Download complete!"
echo "Files saved to: $LOCAL_DIR"
```

### Script 3: Remote Train Command

**`scripts/remote_train.sh`:**
```bash
#!/bin/bash
# Train VAE on remote cloud GPU

CLOUD_HOST="vast-listener"
EPOCHS=${1:-50}
BATCH_SIZE=${2:-64}

echo "Starting remote training on $CLOUD_HOST..."
echo "Epochs: $EPOCHS, Batch size: $BATCH_SIZE"

ssh $CLOUD_HOST "cd ~/weather-nft-live/listener && \
    python scripts/train.py \
    --data data/sessions \
    --epochs $EPOCHS \
    --batch-size $BATCH_SIZE \
    --output outputs/checkpoints/model_remote_$(date +%Y%m%d_%H%M%S).pt"

echo "✓ Training complete! Downloading checkpoint..."
bash scripts/sync_from_cloud.sh
```

**Usage:**
```bash
# Train with default params (50 epochs, batch 64)
bash scripts/remote_train.sh

# Train with custom params (100 epochs, batch 32)
bash scripts/remote_train.sh 100 32
```

---

## Security Best Practices

### 1. SSH Key Authentication

**Generate SSH key:**
```bash
ssh-keygen -t ed25519 -C "listener-cloud"
```

**Add to vast.ai instance:**
```bash
# Copy public key
cat ~/.ssh/id_ed25519.pub

# On vast.ai dashboard, add to "SSH Public Keys"
```

### 2. Environment Variables

**Don't commit API keys!**

**On cloud GPU:**
```bash
# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=your_key_here
REPLICATE_API_TOKEN=your_token_here
EOF

# Make sure .gitignore includes .env
echo ".env" >> .gitignore
```

### 3. Firewall Rules

**On vast.ai:**
- Only expose SSH (port 22) and Jupyter (port 8080)
- Don't expose unnecessary ports
- Use SSH tunneling for services

---

## Troubleshooting

### Issue: Instance Interrupted (vast.ai)

**Solution:**
```
1. Enable checkpointing in training scripts (already done!)
2. Use interruptible-safe workflows
3. Download checkpoints frequently
4. Consider RunPod for mission-critical work
```

### Issue: Slow Upload/Download

**Solution:**
```bash
# Compress before transfer
tar -czf sessions.tar.gz data/sessions/
rsync -avz sessions.tar.gz vast-listener:~/
ssh vast-listener "tar -xzf sessions.tar.gz"

# Or use faster compression
tar -cf - data/sessions/ | pigz | ssh vast-listener "cat > sessions.tar.gz"
```

### Issue: Out of Disk Space

**Solution:**
```bash
# SSH to cloud
ssh vast-listener

# Clean up
rm -rf ~/.cache/huggingface/  # Downloaded models
rm -rf outputs/old_*/          # Old outputs
df -h  # Check space
```

### Issue: Can't Connect to Jupyter

**Solution:**
```bash
# Check port forwarding
ssh -L 8080:localhost:8080 vast-listener

# Or use VSCode Remote SSH (easier)
```

---

## Comparison: Local vs Cloud vs Hybrid

| Aspect | Local Only | Cloud Only | Hybrid (Recommended) |
|--------|-----------|------------|---------------------|
| **EEG Capture** | ✅ Must be local | ❌ Impossible | ✅ Local |
| **Preprocessing** | ✅ Free | ⚠️ Costs $ | ✅ Local (free) |
| **VAE Training** | ⚠️ Slow | ✅ Fast | ✅ Cloud when needed |
| **Image Gen** | ⚠️ Limited | ✅ Fast | ✅ Cloud for batches |
| **Video Gen** | ⚠️ CPU only | ✅ Fast GPU | ✅ Cloud for quality |
| **Analysis** | ✅ Free | ⚠️ Costs $ | ✅ Local (free) |
| **Cost** | ✅ Free | ⚠️ $$$ | ✅ $ (optimal) |
| **Speed** | ⚠️ Slow | ✅ Very fast | ✅ Best of both |
| **Flexibility** | ⚠️ Limited | ✅ Any GPU | ✅ Maximum |

---

## Recommended Setup

**For THE LISTENER Project:**

1. **Local (Your Windows/WSL Machine):**
   - Muse S EEG capture
   - MNE preprocessing
   - Feature extraction
   - Daily meditation analysis
   - Code development

2. **Cloud GPU (vast.ai RTX 3090):**
   - Weekly VAE training on accumulated sessions
   - Monthly batch image/video generation
   - Model experimentation
   - Final exhibition piece generation

3. **Cost Estimate:**
   - 8-month project (60 sessions)
   - ~2-4 hours/month on cloud GPU
   - Total cost: ~$5-10 for entire project
   - vs Local only: Free but much slower
   - vs Cloud only: ~$20-50 (unnecessary expense)

**Best of both worlds!** 🎉

---

## Quick Start Checklist

- [ ] Create vast.ai account
- [ ] Add $10 credit
- [ ] Launch RTX 3090 instance
- [ ] Setup SSH config
- [ ] Clone repository on cloud
- [ ] Install dependencies
- [ ] Test GPU setup
- [ ] Create sync scripts
- [ ] Upload first session
- [ ] Run test training
- [ ] Download results
- [ ] Verify workflow works
- [ ] Destroy instance (save money)
- [ ] Ready for production!

---

**Next Steps:** Try it out with one session to validate the workflow, then scale up!
