#!/bin/bash
# Switch from Mock SD AI to Real SD AI

echo "🔄 Switching to Real SD AI Server"
echo "=================================="
echo ""

# Stop mock server
echo "Stopping SD AI Mock server..."
pkill -f "simple-sd-ai-mock.py" && echo "✅ Mock server stopped" || echo "ℹ️ Mock server was not running"

# Wait a moment
sleep 2

# Check if real SD AI is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Real SD AI server is already running!"
    
    # Test the real server
    echo ""
    echo "Testing real SD AI server..."
    health_response=$(curl -s http://localhost:8000/health)
    echo "Health check: $health_response"
    
else
    echo "❌ Real SD AI server is not running"
    echo ""
    echo "To start real SD AI server:"
    echo "1. Open PowerShell/CMD in Windows"
    echo "2. Navigate to project directory"
    echo "3. Run: conda activate SD"
    echo "4. Run: pip install fastapi uvicorn (if not installed)"
    echo "5. Run: python sd-pytorch-integration.py --server"
    echo ""
    echo "Or run the install script: install-sd-api-deps.bat"
fi

echo ""
echo "📊 Admin panel will now connect to:"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Real SD AI Server (http://localhost:8000)"
else
    echo "❌ No SD AI server available"
    echo "   Starting mock server as fallback..."
    nohup python3 simple-sd-ai-mock.py > logs/sd-ai.log 2>&1 &
    sleep 2
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Mock SD AI Server (http://localhost:8000)"
    fi
fi

echo ""