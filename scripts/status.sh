#!/bin/bash
# WeatherNFT - Check Services Status

echo "🌦️ WeatherNFT - Service Status"
echo "==============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check service
check_service() {
    local service_name=$1
    local port=$2
    local process_name=$3
    
    # Check if process is running
    if ps aux | grep "$process_name" | grep -v grep > /dev/null 2>&1; then
        # Check if port is listening
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name${NC} - Running on port $port"
            
            # Try to get health status
            if [ "$port" == "3006" ] || [ "$port" == "3007" ] || [ "$port" == "3008" ]; then
                health=$(curl -s http://localhost:$port/health 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
                if [ ! -z "$health" ]; then
                    echo -e "   Health: ${GREEN}$health${NC}"
                fi
            fi
        else
            echo -e "${YELLOW}⚠️  $service_name${NC} - Process running but port $port not listening"
        fi
    else
        echo -e "${RED}❌ $service_name${NC} - Not running"
    fi
}

# Function to check URL
check_url() {
    local name=$1
    local url=$2
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|301\|302"; then
        echo -e "   ${GREEN}✓${NC} $name: $url"
    else
        echo -e "   ${RED}✗${NC} $name: $url"
    fi
}

# Check all services
echo -e "${BLUE}Services:${NC}"
check_service "AI Backend" 3006 "simple-test-server.js"
check_service "Blockchain Service" 3007 "blockchain-service.js"
check_service "Admin Backend" 3008 "admin-backend.js"
check_service "Frontend Server" 8081 "simple-frontend-server.js"
check_service "SD AI Mock" 8000 "simple-sd-ai-mock.py"

echo ""
echo -e "${BLUE}Web Access:${NC}"
check_url "Frontend" "http://localhost:8081/"
check_url "Admin Panel" "http://localhost:8081/admin-futuristic.html"

echo ""
echo -e "${BLUE}API Endpoints:${NC}"
# Check API endpoints
if curl -s http://localhost:3006/api/events > /dev/null 2>&1; then
    events_count=$(curl -s http://localhost:3006/api/events | grep -o '"count":[0-9]*' | cut -d: -f2)
    echo -e "   ${GREEN}✓${NC} AI Events: $events_count active events"
else
    echo -e "   ${RED}✗${NC} AI Events API not accessible"
fi

if curl -s http://localhost:3008/api/dashboard > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Admin Dashboard API working"
else
    echo -e "   ${RED}✗${NC} Admin Dashboard API not accessible"
fi

echo ""
echo -e "${BLUE}System Resources:${NC}"
# Count total processes
total_processes=$(ps aux | grep -E "(node|python3).*(weather|simple-test|blockchain|admin)" | grep -v grep | wc -l)
echo "   Running processes: $total_processes"

# Show memory usage
if command -v free >/dev/null 2>&1; then
    mem_used=$(free -m | awk 'NR==2{printf "%.1f", $3/1024}')
    mem_total=$(free -m | awk 'NR==2{printf "%.1f", $2/1024}')
    echo "   Memory usage: ${mem_used}GB / ${mem_total}GB"
fi

echo ""
echo -e "${BLUE}Quick Actions:${NC}"
echo "   • Start all: ./restart-all.sh"
echo "   • Stop all: ./stop-all.sh"
echo "   • View logs: tail -f logs/*.log"
echo ""