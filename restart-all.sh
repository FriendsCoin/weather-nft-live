#!/bin/bash
# WeatherNFT - Restart All Services Script

echo "🌦️ WeatherNFT Service Manager"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to kill process by name
kill_process() {
    local process_name=$1
    local pids=$(ps aux | grep "$process_name" | grep -v grep | awk '{print $2}')
    
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}Stopping $process_name...${NC}"
        for pid in $pids; do
            kill $pid 2>/dev/null && echo -e "${GREEN}  ✓ Killed PID $pid${NC}" || echo -e "${RED}  ✗ Failed to kill PID $pid${NC}"
        done
    fi
}

# Function to check if port is free
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}  ✗ Port $port is already in use${NC}"
        return 1
    else
        echo -e "${GREEN}  ✓ Port $port is free${NC}"
        return 0
    fi
}

# Function to start service
start_service() {
    local name=$1
    local command=$2
    local port=$3
    local log_file=$4
    
    echo -e "${BLUE}Starting $name on port $port...${NC}"
    
    if check_port $port; then
        nohup $command > "$log_file" 2>&1 &
        local pid=$!
        sleep 2
        
        if ps -p $pid > /dev/null; then
            echo -e "${GREEN}  ✓ $name started (PID: $pid)${NC}"
            return 0
        else
            echo -e "${RED}  ✗ $name failed to start${NC}"
            return 1
        fi
    else
        echo -e "${RED}  ✗ Cannot start $name - port $port is busy${NC}"
        return 1
    fi
}

# Stop all services
echo -e "${YELLOW}🛑 Stopping all services...${NC}"
echo ""

kill_process "simple-test-server.js"
kill_process "blockchain-service.js"
kill_process "admin-backend.js"
kill_process "simple-frontend-server.js"
kill_process "simple-sd-ai-mock.py"
kill_process "sd-pytorch-integration.py"
kill_process "python3 -m http.server 8080"

# Wait for processes to stop
sleep 3

echo ""
echo -e "${BLUE}🚀 Starting all services...${NC}"
echo ""

# Create logs directory
mkdir -p logs

# Start services
services_started=0

# AI Backend
if start_service "AI Backend" "node simple-test-server.js" 3006 "logs/ai-backend.log"; then
    ((services_started++))
fi

# Blockchain Service
if start_service "Blockchain Service" "node blockchain-service.js" 3007 "logs/blockchain.log"; then
    ((services_started++))
fi

# Admin Backend
if start_service "Admin Backend" "node admin-backend.js" 3008 "logs/admin-backend.log"; then
    ((services_started++))
fi

# Frontend Server
if start_service "Frontend Server" "node simple-frontend-server.js" 8081 "logs/frontend.log"; then
    ((services_started++))
fi

# SD AI Mock Server
if start_service "SD AI Mock" "python3 simple-sd-ai-mock.py" 8000 "logs/sd-ai.log"; then
    ((services_started++))
fi

# Summary
echo ""
echo -e "${GREEN}=============================="
echo -e "✅ Started $services_started/5 services"
echo -e "==============================${NC}"
echo ""
echo "📊 Service URLs:"
echo "  • Frontend: http://localhost:8081"
echo "  • Admin Panel: http://localhost:8081/admin-futuristic.html"
echo "  • AI Backend: http://localhost:3006"
echo "  • Blockchain: http://localhost:3007"
echo "  • Admin API: http://localhost:3008"
echo "  • SD AI Mock: http://localhost:8000"
echo ""
echo "📁 Logs are in the 'logs' directory"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo "  • View logs: tail -f logs/*.log"
echo "  • Stop all: ./stop-all.sh"
echo "  • Check status: ./status.sh"
echo ""