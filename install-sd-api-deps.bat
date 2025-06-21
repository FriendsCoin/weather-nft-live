@echo off
echo 🔧 Installing SD AI API Dependencies
echo ===================================

REM Activate SD environment
call conda activate SD

REM Install required packages
echo Installing FastAPI and dependencies...
pip install fastapi
pip install "uvicorn[standard]"
pip install aiohttp
pip install python-multipart

echo.
echo ✅ Installation complete!
echo.
echo You can now run:
echo   python sd-pytorch-integration.py --server
echo.
pause