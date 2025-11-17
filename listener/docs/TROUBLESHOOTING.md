# THE LISTENER - Troubleshooting Guide

Common issues and their solutions.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Data Processing Issues](#data-processing-issues)
- [GPU and CUDA Issues](#gpu-and-cuda-issues)
- [API Issues](#api-issues)
- [Model Training Issues](#model-training-issues)
- [Real-time Feedback Issues](#real-time-feedback-issues)
- [Performance Issues](#performance-issues)

---

## Installation Issues

### Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'torch'
```

**Solution:**
```bash
# Install all requirements
pip install -r requirements.txt

# Or install specific package
pip install torch
```

### Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'data/sessions'
```

**Solution:**
```bash
# Check directory permissions
ls -la data/

# Fix permissions
chmod -R u+w data/

# Or run setup script to recreate directories
python scripts/setup.py
```

### Python Version Issues

**Error:**
```
SyntaxError: invalid syntax
```

**Solution:**
THE LISTENER requires Python 3.8+

```bash
# Check your Python version
python --version

# Use Python 3.8 or higher
python3.8 -m pip install -r requirements.txt
python3.8 scripts/train.py
```

---

## Configuration Issues

### Config File Not Found

**Error:**
```
Configuration file not found: config.yaml
```

**Solution:**
```bash
# Run setup wizard
python scripts/setup.py

# Or copy example config
cp config.example.yaml config.yaml

# Then edit with your settings
nano config.yaml
```

### Invalid YAML Syntax

**Error:**
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Solution:**
Check your YAML syntax. Common mistakes:
- Missing spaces after colons
- Incorrect indentation (use spaces, not tabs)
- Unquoted strings with special characters

```yaml
# ✗ Wrong
api_key:your-key-here
model:
  latent_dim:32

# ✓ Correct
api_key: "your-key-here"
model:
  latent_dim: 32
```

### API Keys Not Working

**Error:**
```
API authentication failed
```

**Solution:**
1. Check that API keys in `config.yaml` don't have quotes or spaces:
```yaml
# ✗ Wrong
api_key: "'your-key-123'"

# ✓ Correct
api_key: "your-key-123"
```

2. Verify your API keys are valid:
   - Anthropic: https://console.anthropic.com/
   - Replicate: https://replicate.com/account

3. Check API credits/quota

---

## Data Processing Issues

### No Data Files Found

**Error:**
```
No feature files found in data/sessions
```

**Solution:**
```bash
# Generate sample data first
python scripts/generate_mock_data.py --num-sessions 5 --duration 300

# Check data was created
ls data/raw/sessions/
```

### Corrupted Session Data

**Error:**
```
Failed to validate session data: EOFError
```

**Solution:**
```bash
# Clear cache
python -c "from src.utils.caching import clear_all_caches; clear_all_caches()"

# Regenerate the session
python scripts/generate_mock_data.py --num-sessions 1 --duration 300

# If using real data, re-record the session
```

### Preprocessing Fails

**Error:**
```
ValueError: Input signal length must be greater than filter order
```

**Solution:**
Your session may be too short. EEG preprocessing requires at least 10 seconds of data.

```bash
# Generate longer sessions
python scripts/generate_mock_data.py --duration 300  # 5 minutes

# Or check your real recording duration
```

---

## GPU and CUDA Issues

### CUDA Out of Memory

**Error:**
```
RuntimeError: CUDA out of memory
```

**Solution:**
```bash
# 1. Reduce batch size
python scripts/train.py --batch-size 16

# 2. Reduce latent dimension
python scripts/train.py --latent-dim 16

# 3. Use CPU instead
python scripts/train.py --device cpu

# 4. Clear GPU memory
python -c "import torch; torch.cuda.empty_cache()"
```

### CUDA Not Available

**Error:**
```
CUDA not available - using CPU
```

**Solution:**
```bash
# 1. Check NVIDIA driver
nvidia-smi

# 2. Check PyTorch CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# 3. Reinstall PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 4. Test GPU setup
python scripts/test_gpu_setup.py
```

### Wrong CUDA Version

**Error:**
```
CUDA driver version is insufficient for CUDA runtime version
```

**Solution:**
```bash
# Check CUDA version
nvidia-smi  # Look for "CUDA Version: X.X"

# Install matching PyTorch version
# For CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# See: https://pytorch.org/get-started/locally/
```

---

## API Issues

### Anthropic API Rate Limit

**Error:**
```
anthropic.RateLimitError: Rate limit exceeded
```

**Solution:**
```bash
# 1. Reduce number of memories generated
python scripts/generate_memories.py --num-memories 1

# 2. Add delay between calls (automatically handled)

# 3. Check your API tier limits at console.anthropic.com
```

### Replicate API Timeout

**Error:**
```
replicate.exceptions.ReplicateError: Prediction timed out
```

**Solution:**
```bash
# 1. Use local Stable Diffusion instead
python scripts/generate_memories.py --local-sd

# 2. Reduce image quality
# Edit config.yaml:
image_generation:
  num_inference_steps: 25  # Reduced from 50

# 3. Check Replicate status: https://status.replicate.com/
```

### Network Connection Issues

**Error:**
```
requests.exceptions.ConnectionError: Failed to establish a new connection
```

**Solution:**
```bash
# 1. Check internet connection
ping google.com

# 2. Check if behind proxy
# Set proxy environment variables:
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"

# 3. Use local-only mode
python scripts/setup.py --skip-api-keys
```

---

## Model Training Issues

### Training Not Converging

**Symptom:** Loss stays high or doesn't decrease

**Solution:**
```bash
# 1. Check if you have enough data (need at least 60 sessions for good results)
ls data/raw/sessions/ | wc -l

# 2. Try different learning rate
python scripts/train.py --lr 0.0001  # Lower
python scripts/train.py --lr 0.01    # Higher

# 3. Increase epochs
python scripts/train.py --epochs 200

# 4. Reduce latent dimension for small datasets
python scripts/train.py --latent-dim 16
```

### NaN Loss During Training

**Error:**
```
Loss became NaN at epoch 15
```

**Solution:**
```bash
# 1. Reduce learning rate
python scripts/train.py --lr 0.0001

# 2. Check data quality
python scripts/analyze_meditation.py data/raw/sessions/session_001.pkl

# 3. Regenerate data if using mock data
python scripts/generate_mock_data.py --num-sessions 5 --duration 300
```

### Checkpoint Not Saving

**Error:**
```
Permission denied: 'data/checkpoints/vae_epoch_10.pt'
```

**Solution:**
```bash
# Create checkpoint directory
mkdir -p data/checkpoints

# Fix permissions
chmod -R u+w data/checkpoints/

# Or specify different directory
python scripts/train.py --checkpoint-dir /tmp/checkpoints
```

---

## Real-time Feedback Issues

### Muse Headband Not Connecting

**Error:**
```
Bluetooth connection failed: Device not found
```

**Solution:**
```bash
# 1. Check Bluetooth is enabled
bluetoothctl power on

# 2. Scan for devices
bluetoothctl scan on

# 3. Check device name in config.yaml
muse:
  device_name: "Muse-XXXX"  # Match your device name exactly

# 4. Pair device first
bluetoothctl pair XX:XX:XX:XX:XX:XX

# 5. Test with mock data first
python scripts/realtime_feedback.py --mock
```

### Real-time Lag/Delay

**Symptom:** Feedback is delayed by several seconds

**Solution:**
```bash
# 1. Reduce processing window
# Edit config.yaml:
features:
  window_size: 2.0  # Reduced from 4.0

# 2. Use GPU for faster processing
python scripts/realtime_feedback.py --device cuda

# 3. Reduce feature computation
# Edit config.yaml:
features:
  compute_connectivity: false  # Expensive
```

### Feedback States Jumping Around

**Symptom:** State changes too frequently (a+, a-, b+, b- rapidly switching)

**Solution:**
```bash
# 1. Increase smoothing window
# In realtime_feedback.py, increase smoothing

# 2. Use baseline calibration
python scripts/realtime_feedback.py --baseline data/baselines/baseline_001.pkl

# 3. Check electrode contact quality
# Poor contact causes noisy signals
```

---

## Performance Issues

### Slow Feature Extraction

**Symptom:** Processing takes minutes per session

**Solution:**
```bash
# 1. Enable caching
from src.utils.caching import SessionCache
cache = SessionCache()  # Automatically used

# 2. Use GPU
python scripts/process_session.py --device cuda

# 3. Reduce feature complexity
# Edit config.yaml:
features:
  compute_connectivity: false
  compute_entropy: false
```

### High Memory Usage

**Symptom:** System runs out of RAM

**Solution:**
```bash
# 1. Process sessions one at a time instead of batch
for session in data/raw/sessions/*.pkl; do
    python scripts/process_session.py "$session"
done

# 2. Reduce batch size in training
python scripts/train.py --batch-size 8

# 3. Use smaller model
python scripts/train.py --latent-dim 16 --encoder-layers 64,32
```

### Slow Image Generation

**Symptom:** Stable Diffusion takes minutes per image

**Solution:**
```bash
# 1. Use cloud API instead of local
# Remove --local-sd flag

# 2. Reduce inference steps
# Edit config.yaml:
image_generation:
  num_inference_steps: 25

# 3. Use faster model
# Edit config.yaml:
replicate:
  model: "stability-ai/sdxl-turbo"  # Faster variant
```

---

## General Debugging

### Enable Debug Logging

```python
# Add to your script:
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or edit `config.yaml`:
```yaml
project:
  log_level: "DEBUG"
```

### Get System Information

```bash
# Run diagnostics
python scripts/test_gpu_setup.py

# Or in Python:
python -c "from src.utils.error_handling import print_system_info; print_system_info()"
```

### Check Cache

```bash
# View cache statistics
python -c "from src.utils.caching import get_cache_stats; print(get_cache_stats())"

# Clear all caches
python -c "from src.utils.caching import clear_all_caches; clear_all_caches()"
```

### Still Having Issues?

1. Check the logs: `cat logs/listener.log`
2. Run with verbose output: `python scripts/[script].py --verbose`
3. Check documentation: `docs/TECHNICAL.md`
4. Generate a bug report:
```bash
python -c "
from src.utils.error_handling import print_system_info
import sys
print_system_info()
print('Python path:', sys.executable)
"
```

---

## Common Workflow Issues

### "I want to skip API costs and work locally"

```bash
# Setup without API keys
python scripts/setup.py --skip-api-keys

# Train model locally
python scripts/generate_mock_data.py --num-sessions 10
python scripts/train.py

# Visualize without text/images
python scripts/visualize.py
```

### "My meditation analysis looks random"

This is normal if:
- You're using mock data (it's random by design)
- You haven't done baseline calibration
- You have less than 3-5 real sessions

Solution:
```bash
# Record a proper baseline (5-10 minutes, eyes open, relaxed)
python scripts/record_baseline.py

# Then use it for analysis
python scripts/analyze_meditation.py session.pkl --baseline data/baselines/baseline_001.pkl
```

### "Training loss is 0 or very small"

This might indicate:
- Overfitting (too little data)
- Data leak (train/val split issue)

Solution:
```bash
# Generate more diverse data
python scripts/generate_mock_data.py --num-sessions 50 --duration 600

# Retrain with validation
python scripts/train.py --epochs 100
```

---

## Getting Help

If you're still stuck:

1. **Check the error message carefully** - it often contains the solution
2. **Review documentation** - `docs/` folder has detailed guides
3. **Check config** - many issues are configuration-related
4. **Start simple** - use mock data and default settings first
5. **Enable debug logging** - see what's happening under the hood

The enhanced error handling system will provide specific solutions for most common issues!
