#!/bin/bash
# Train VAE on remote cloud GPU
# Usage: ./remote_train.sh [host] [epochs] [batch_size]

set -e

# Configuration
CLOUD_HOST="${1:-vast-listener}"
EPOCHS="${2:-50}"
BATCH_SIZE="${3:-64}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  THE LISTENER - Remote Training${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo "Configuration:"
echo "  Host:       $CLOUD_HOST"
echo "  Epochs:     $EPOCHS"
echo "  Batch size: $BATCH_SIZE"
echo ""

# Check connection
echo -e "${BLUE}→${NC} Checking connection..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $CLOUD_HOST exit 2>/dev/null; then
    echo "❌ Cannot connect to $CLOUD_HOST"
    exit 1
fi
echo -e "${GREEN}✓${NC} Connected!"
echo ""

# Check if data exists on remote
echo -e "${BLUE}→${NC} Checking remote data..."
SESSION_COUNT=$(ssh $CLOUD_HOST "ls ~/weather-nft-live/listener/data/sessions/*.h5 2>/dev/null | wc -l" || echo "0")

if [ "$SESSION_COUNT" -eq "0" ]; then
    echo -e "${YELLOW}⚠${NC}  No session data found on remote!"
    echo ""
    echo "Please run sync first:"
    echo "  ./scripts/cloud/sync_to_cloud.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} Found $SESSION_COUNT sessions"
echo ""

# Generate unique model name
MODEL_NAME="model_$(date +%Y%m%d_%H%M%S).pt"

# Start training
echo -e "${BLUE}→${NC} Starting remote training..."
echo "   Model will be saved as: outputs/checkpoints/$MODEL_NAME"
echo ""
echo "───────────────────────────────────────────────"
echo ""

ssh $CLOUD_HOST "cd ~/weather-nft-live/listener && \
    python scripts/train.py \
    --data data/sessions \
    --epochs $EPOCHS \
    --batch-size $BATCH_SIZE \
    --output outputs/checkpoints/$MODEL_NAME"

echo ""
echo "───────────────────────────────────────────────"
echo ""
echo -e "${GREEN}✓${NC} Training complete!"
echo ""

# Ask to download
read -p "Download checkpoint now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}→${NC} Downloading checkpoint..."
    ./scripts/cloud/sync_from_cloud.sh $CLOUD_HOST
fi

echo ""
echo "✨ Done! Your model is ready."
echo ""
