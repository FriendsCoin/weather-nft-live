#!/bin/bash
# Download results from cloud GPU instance
# Usage: ./sync_from_cloud.sh [host]

set -e

# Configuration
CLOUD_HOST="${1:-vast-listener}"
REMOTE_DIR="~/weather-nft-live/listener/outputs"
LOCAL_DIR="outputs"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  THE LISTENER - Sync from Cloud${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Check connection
echo -e "${BLUE}→${NC} Checking connection to $CLOUD_HOST..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $CLOUD_HOST exit 2>/dev/null; then
    echo "❌ Cannot connect to $CLOUD_HOST"
    echo "   Is your cloud instance running?"
    exit 1
fi
echo -e "${GREEN}✓${NC} Connected!"
echo ""

# Check if remote directory exists
echo -e "${BLUE}→${NC} Checking remote outputs..."
if ! ssh $CLOUD_HOST "[ -d $REMOTE_DIR ]" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  No outputs found on remote"
    echo "   Have you run any training or generation yet?"
    exit 0
fi

# Count remote files
REMOTE_COUNT=$(ssh $CLOUD_HOST "find $REMOTE_DIR -type f 2>/dev/null | wc -l")
echo -e "${BLUE}→${NC} Found $REMOTE_COUNT files to download"
echo ""

# Create local directory if needed
mkdir -p $LOCAL_DIR

# Download
echo -e "${BLUE}→${NC} Downloading from $CLOUD_HOST:$REMOTE_DIR..."
echo ""
rsync -avz --progress \
    --exclude='*.tmp' \
    --exclude='__pycache__' \
    $CLOUD_HOST:$REMOTE_DIR/ \
    $LOCAL_DIR/

echo ""
echo -e "${GREEN}✓${NC} Download complete!"
echo ""
echo "Results saved to: $LOCAL_DIR"
echo ""
echo "Next steps:"
echo "  1. Review outputs: ls -lh $LOCAL_DIR"
echo "  2. Run analysis: python scripts/analyze_meditation.py ..."
echo "  3. Consider destroying cloud instance to save money!"
echo ""
