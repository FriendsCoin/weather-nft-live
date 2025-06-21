#!/bin/bash
# Railway startup script for all services

echo "🚀 Starting WeatherNFT on Railway"
echo "=================================="

# Start AI Backend
echo "Starting AI Backend..."
node simple-test-server.js &
AI_PID=$!

# Start Blockchain Service
echo "Starting Blockchain Service..."
node blockchain-service.js &
BLOCKCHAIN_PID=$!

# Start Admin Backend
echo "Starting Admin Backend..."
node admin-backend.js &
ADMIN_PID=$!

# Start Frontend Server (main)
echo "Starting Frontend Server..."
PORT=${PORT:-8080} node simple-frontend-server.js &
FRONTEND_PID=$!

# Wait for services to start
sleep 5

echo "✅ All services started"
echo "Frontend: http://localhost:${PORT:-8080}"
echo "AI Backend: http://localhost:3006"
echo "Blockchain: http://localhost:3007"
echo "Admin API: http://localhost:3008"

# Keep the container running
wait $FRONTEND_PID