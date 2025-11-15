#!/bin/bash

echo "🔥 Starting WeatherNFT PyTorch AI Server"
echo "====================================="

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Anaconda/Miniconda"
    exit 1
fi

# Activate SD environment
echo "Activating Anaconda SD environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate SD

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate SD environment"
    echo "Make sure SD environment exists: conda env list"
    exit 1
fi

echo "✅ SD environment activated"

# Install additional packages
echo "Installing additional packages..."
pip install fastapi uvicorn aiohttp python-dotenv --quiet

# Set environment variables
export OPENWEATHER_API_KEY="your_api_key_here"
export PYTORCH_AI_PORT=8000

echo "🧠 Starting PyTorch AI Server on port $PYTORCH_AI_PORT"
echo "Available endpoints:"
echo "  • POST /predict - Predict weather events"
echo "  • POST /train - Train model"  
echo "  • GET /health - Health check"
echo "  • GET /model/info - Model information"
echo ""

# Start the PyTorch server
python pytorch-api-integration.py