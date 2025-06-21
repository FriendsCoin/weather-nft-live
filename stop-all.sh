#!/bin/bash
# WeatherNFT - Stop All Services Script

echo "🌦️ WeatherNFT - Stopping All Services"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to kill process by name
kill_process() {
    local process_name=$1
    local display_name=$2
    local pids=$(ps aux | grep "$process_name" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}Stopping $display_name...${NC}"
        for pid in $pids; do
            kill $pid 2>/dev/null && echo -e "${GREEN}  ✓ Stopped PID $pid${NC}" || echo -e "${RED}  ✗ Failed to stop PID $pid${NC}"
        done
    else
        echo -e "${YELLOW}$display_name not running${NC}"
    fi
}

# Stop all services
kill_process "simple-test-server.js" "AI Backend"
kill_process "blockchain-service.js" "Blockchain Service"
kill_process "admin-backend.js" "Admin Backend"
kill_process "simple-frontend-server.js" "Frontend Server"
kill_process "simple-sd-ai-mock.py" "SD AI Mock"
kill_process "sd-pytorch-integration.py" "SD PyTorch AI"
kill_process "python3 -m http.server 8080" "Python HTTP Server"

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""