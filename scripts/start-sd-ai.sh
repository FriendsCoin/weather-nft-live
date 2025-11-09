#!/bin/bash
# WeatherNFT.live - SD Environment AI Launcher
echo "🌦️ WeatherNFT.live - SD PyTorch AI Integration"
echo "=============================================="

# Check if we're in WSL/Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Linux/WSL environment detected"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "🪟 Windows environment detected"
fi

# Function to check and activate conda
activate_conda() {
    echo "🔍 Checking for conda installation..."
    
    # Common conda paths
    CONDA_PATHS=(
        "$HOME/anaconda3/bin/conda"
        "$HOME/miniconda3/bin/conda"
        "/opt/anaconda3/bin/conda"
        "/opt/miniconda3/bin/conda"
        "/c/Users/$USER/anaconda3/Scripts/conda.exe"
        "/c/ProgramData/Anaconda3/Scripts/conda.exe"
    )
    
    for conda_path in "${CONDA_PATHS[@]}"; do
        if [[ -f "$conda_path" ]]; then
            echo "✅ Found conda at: $conda_path"
            export PATH="$(dirname "$conda_path"):$PATH"
            
            # Initialize conda for bash
            eval "$($conda_path shell.bash hook)" 2>/dev/null
            
            echo "🔄 Attempting to activate SD environment..."
            
            # Try different SD environment names
            SD_ENVS=("SD" "sd" "stable-diffusion" "automatic1111" "webui")
            
            for env_name in "${SD_ENVS[@]}"; do
                if conda env list | grep -q "^$env_name "; then
                    echo "✅ Found SD environment: $env_name"
                    conda activate "$env_name"
                    if [[ $? -eq 0 ]]; then
                        echo "✅ SD environment activated successfully"
                        return 0
                    fi
                fi
            done
            
            echo "⚠️ No SD environment found, using base environment"
            return 1
        fi
    done
    
    echo "❌ Conda not found in common locations"
    return 1
}

# Function to install Python dependencies
install_dependencies() {
    echo "📦 Installing Python dependencies..."
    
    # Essential packages
    PACKAGES=(
        "torch"
        "torchvision" 
        "fastapi"
        "uvicorn"
        "aiohttp"
        "numpy"
        "pandas"
    )
    
    for package in "${PACKAGES[@]}"; do
        echo "   Installing $package..."
        python -m pip install "$package" --quiet --user 2>/dev/null || {
            echo "   ⚠️ Failed to install $package - continuing..."
        }
    done
    
    echo "✅ Dependencies installation completed"
}

# Function to check Python and PyTorch
check_python() {
    echo "🐍 Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "❌ Python not found"
        return 1
    fi
    
    echo "✅ Python found: $($PYTHON_CMD --version)"
    
    # Check PyTorch
    echo "🧠 Checking PyTorch..."
    $PYTHON_CMD -c "import torch; print(f'✅ PyTorch {torch.__version__} available')" 2>/dev/null || {
        echo "⚠️ PyTorch not available - will use fallback mode"
        return 1
    }
    
    # Check CUDA
    $PYTHON_CMD -c "import torch; print(f'🔥 CUDA: {torch.cuda.is_available()}')" 2>/dev/null || {
        echo "⚠️ CUDA check failed"
    }
    
    return 0
}

# Function to start the AI server
start_ai_server() {
    echo "🚀 Starting WeatherNFT AI Server..."
    
    # Set environment variables
    export PYTORCH_AI_PORT=8000
    export PYTHONPATH="$PWD:$PYTHONPATH"
    
    echo "📊 Server configuration:"
    echo "   Port: $PYTORCH_AI_PORT"
    echo "   Working directory: $PWD"
    echo "   Python: $PYTHON_CMD"
    echo ""
    
    echo "🌐 Available endpoints:"
    echo "   • GET  /health      - Health check"
    echo "   • GET  /model/info  - Model information"
    echo "   • POST /predict     - Weather prediction"
    echo "   • Docs: http://localhost:$PYTORCH_AI_PORT/docs"
    echo ""
    
    # Start the server
    if [[ "$1" == "--server" ]]; then
        echo "🔥 Starting API server mode..."
        $PYTHON_CMD sd-pytorch-integration.py --server
    else
        echo "🧪 Running test mode..."
        $PYTHON_CMD sd-pytorch-integration.py
        echo ""
        echo "💡 To start API server: $0 --server"
    fi
}

# Main execution
main() {
    # Try to activate conda SD environment
    activate_conda
    
    # Check Python and PyTorch
    if check_python; then
        echo "✅ Python environment ready"
    else
        echo "⚠️ Python environment issues detected"
        echo "🔧 Attempting to install dependencies..."
        install_dependencies
    fi
    
    # Start the AI server
    start_ai_server "$1"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi