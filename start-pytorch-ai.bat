@echo off
echo 🔥 Starting WeatherNFT PyTorch AI Server
echo =====================================

REM Activate Anaconda SD environment
echo Activating Anaconda SD environment...
call conda activate SD

REM Check if environment activated
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to activate SD environment
    echo Make sure Anaconda is installed and SD environment exists
    pause
    exit /b 1
)

echo ✅ SD environment activated

REM Install additional packages if needed
echo Installing additional packages...
pip install fastapi uvicorn aiohttp python-dotenv --quiet

REM Set environment variables
set OPENWEATHER_API_KEY=your_api_key_here
set PYTORCH_AI_PORT=8000

echo 🧠 Starting PyTorch AI Server on port %PYTORCH_AI_PORT%
echo Available endpoints:
echo   • POST /predict - Predict weather events
echo   • POST /train - Train model
echo   • GET /health - Health check
echo   • GET /model/info - Model information
echo.

REM Start the PyTorch server
python pytorch-api-integration.py

pause