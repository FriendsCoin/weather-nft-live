#!/bin/bash
# Quick test for Real SD AI connection

echo "🧪 Testing Real SD AI Connection"
echo "================================"
echo ""

# Test basic connectivity
echo "1. Testing connectivity to port 8000..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Port 8000 is responding"
else
    echo "❌ No response on port 8000"
    echo ""
    echo "🔧 To start Real SD AI:"
    echo "1. Open Windows terminal"
    echo "2. Run: conda activate SD"
    echo "3. Run: python sd-pytorch-integration.py --server"
    exit 1
fi

echo ""
echo "2. Testing health endpoint..."
health_response=$(curl -s http://localhost:8000/health)
echo "Response: $health_response"

# Check if it's real SD AI
if echo "$health_response" | grep -q '"sd_environment": true'; then
    echo "✅ Real SD AI detected!"
elif echo "$health_response" | grep -q '"sd_environment": false'; then
    echo "⚠️  Mock SD AI detected"
else
    echo "❓ Unknown response format"
fi

echo ""
echo "3. Testing prediction endpoint..."
prediction_response=$(curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"temperature": 35, "humidity": 85, "pressure": 995, "wind_speed": 45}')

if echo "$prediction_response" | grep -q '"success": true'; then
    algorithm=$(echo "$prediction_response" | grep -o '"algorithm": "[^"]*"' | cut -d'"' -f4)
    confidence=$(echo "$prediction_response" | grep -o '"confidence": [0-9.]*' | cut -d':' -f2 | tr -d ' ')
    event_type=$(echo "$prediction_response" | grep -o '"event_type": "[^"]*"' | cut -d'"' -f4)
    
    echo "✅ Prediction successful!"
    echo "   Algorithm: $algorithm"
    echo "   Event: $event_type"
    echo "   Confidence: $(echo "$confidence * 100" | bc -l | cut -d'.' -f1)%"
else
    echo "❌ Prediction failed"
    echo "Response: $prediction_response"
fi

echo ""
echo "4. Admin panel integration test..."
admin_response=$(curl -s http://localhost:3008/api/ai/sd-status)
if echo "$admin_response" | grep -q '"success": true'; then
    echo "✅ Admin panel can connect to SD AI"
else
    echo "❌ Admin panel connection failed"
fi

echo ""
echo "📊 Summary:"
echo "===================="
if curl -s http://localhost:8000/health | grep -q '"sd_environment": true'; then
    echo "🔥 Real SD AI is running and accessible!"
    echo "🌐 Admin Panel: http://localhost:8081/admin-futuristic.html"
    echo "📚 API Docs: http://localhost:8000/docs"
else
    echo "🎭 Mock SD AI is running (fallback mode)"
    echo "💡 Start real SD AI in Windows to get full PyTorch power"
fi
echo ""