#!/bin/bash
# Setup cloud GPU instance for THE LISTENER
# Run this on the cloud instance after first login
# Usage: ssh vast-listener < setup_cloud_instance.sh

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  THE LISTENER - Cloud Instance Setup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Check CUDA
echo -e "${BLUE}→${NC} Checking CUDA availability..."
if ! nvidia-smi &>/dev/null; then
    echo "❌ nvidia-smi not found. Is this a GPU instance?"
    exit 1
fi
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo -e "${GREEN}✓${NC} GPU detected!"
echo ""

# Clone repository if not exists
if [ ! -d "weather-nft-live" ]; then
    echo -e "${BLUE}→${NC} Cloning repository..."
    git clone https://github.com/FriendsCoin/weather-nft-live.git
    cd weather-nft-live/listener
else
    echo -e "${BLUE}→${NC} Repository exists, pulling latest..."
    cd weather-nft-live/listener
    git pull
fi

echo -e "${GREEN}✓${NC} Repository ready"
echo ""

# Install dependencies
echo -e "${BLUE}→${NC} Installing dependencies..."
echo "   This may take 5-10 minutes..."
echo ""

pip install --upgrade pip > /dev/null 2>&1

# Install main requirements
pip install -r requirements.txt 2>&1 | grep -v "Requirement already satisfied" | tail -20

# Install GPU requirements
pip install -r requirements-local-gpu.txt 2>&1 | grep -v "Requirement already satisfied" | tail -20

echo ""
echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Create data directories
echo -e "${BLUE}→${NC} Creating data directories..."
mkdir -p data/sessions
mkdir -p data/raw
mkdir -p data/processed
mkdir -p outputs/checkpoints
mkdir -p outputs/images
mkdir -p outputs/videos
echo -e "${GREEN}✓${NC} Directories created"
echo ""

# Test PyTorch CUDA
echo -e "${BLUE}→${NC} Testing PyTorch CUDA..."
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
echo -e "${GREEN}✓${NC} PyTorch CUDA working"
echo ""

# Test GPU setup script
echo -e "${BLUE}→${NC} Running GPU setup test..."
python scripts/test_gpu_setup.py 2>&1 | tail -30
echo ""

# Setup complete
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  1. Upload data from local: ./scripts/cloud/sync_to_cloud.sh"
echo "  2. Train model: python scripts/train.py --data data/sessions"
echo "  3. Generate images: python scripts/generate_multimedia.py ..."
echo "  4. Download results: ./scripts/cloud/sync_from_cloud.sh"
echo ""
echo "Helpful commands:"
echo "  • Monitor GPU: watch -n 1 nvidia-smi"
echo "  • Check disk: df -h"
echo "  • View logs: tail -f outputs/training.log"
echo ""
echo "💡 Remember to destroy the instance when done to save money!"
echo ""
