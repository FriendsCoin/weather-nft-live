#!/bin/bash
# Sync local data to cloud GPU instance
# Usage: ./sync_to_cloud.sh [host]

set -e

# Configuration
CLOUD_HOST="${1:-vast-listener}"
LOCAL_DIR="data/sessions"
REMOTE_DIR="~/weather-nft-live/listener/data/sessions"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  THE LISTENER - Sync to Cloud${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Check if host is reachable
echo -e "${BLUE}→${NC} Checking connection to $CLOUD_HOST..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $CLOUD_HOST exit 2>/dev/null; then
    echo "❌ Cannot connect to $CLOUD_HOST"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check SSH config in ~/.ssh/config"
    echo "  2. Verify instance is running on vast.ai"
    echo "  3. Test manually: ssh $CLOUD_HOST"
    exit 1
fi
echo -e "${GREEN}✓${NC} Connected!"
echo ""

# Check if local directory exists
if [ ! -d "$LOCAL_DIR" ]; then
    echo "❌ Local directory not found: $LOCAL_DIR"
    echo "   Run this script from the listener/ directory"
    exit 1
fi

# Count files to sync
FILE_COUNT=$(find $LOCAL_DIR -type f | wc -l)
echo -e "${BLUE}→${NC} Found $FILE_COUNT files to sync"
echo ""

# Sync
echo -e "${BLUE}→${NC} Syncing $LOCAL_DIR to $CLOUD_HOST:$REMOTE_DIR..."
echo ""
rsync -avz --progress \
    --exclude='*.tmp' \
    --exclude='__pycache__' \
    --exclude='.DS_Store' \
    $LOCAL_DIR/ \
    $CLOUD_HOST:$REMOTE_DIR/

echo ""
echo -e "${GREEN}✓${NC} Sync complete!"
echo ""
echo "Next steps:"
echo "  1. SSH to cloud: ssh $CLOUD_HOST"
echo "  2. Navigate: cd ~/weather-nft-live/listener"
echo "  3. Train or generate: python scripts/train.py ..."
echo ""
