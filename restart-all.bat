@echo off
REM WeatherNFT - Restart All Services (Windows)

echo ======================================
echo WeatherNFT - Restarting All Services
echo ======================================
echo.

REM Kill existing processes
echo Stopping existing services...
taskkill /F /IM node.exe 2>nul && echo Stopped Node.js processes || echo No Node.js processes found
taskkill /F /FI "WINDOWTITLE eq simple-sd-ai-mock.py*" 2>nul
taskkill /F /FI "WINDOWTITLE eq sd-pytorch-integration.py*" 2>nul

REM Wait for processes to stop
timeout /t 3 /nobreak >nul

REM Create logs directory
if not exist logs mkdir logs

echo.
echo Starting services...
echo.

REM Start AI Backend
echo [1/5] Starting AI Backend (port 3006)...
start /B cmd /c "node simple-test-server.js > logs\ai-backend.log 2>&1"
timeout /t 2 /nobreak >nul

REM Start Blockchain Service
echo [2/5] Starting Blockchain Service (port 3007)...
start /B cmd /c "node blockchain-service.js > logs\blockchain.log 2>&1"
timeout /t 2 /nobreak >nul

REM Start Admin Backend
echo [3/5] Starting Admin Backend (port 3008)...
start /B cmd /c "node admin-backend.js > logs\admin-backend.log 2>&1"
timeout /t 2 /nobreak >nul

REM Start Frontend Server
echo [4/5] Starting Frontend Server (port 8081)...
start /B cmd /c "node simple-frontend-server.js > logs\frontend.log 2>&1"
timeout /t 2 /nobreak >nul

REM Start SD AI Mock
echo [5/5] Starting SD AI Mock (port 8000)...
start /B cmd /c "python simple-sd-ai-mock.py > logs\sd-ai.log 2>&1"

echo.
echo ======================================
echo All services started!
echo ======================================
echo.
echo Service URLs:
echo   - Frontend: http://localhost:8081
echo   - Admin Panel: http://localhost:8081/admin-futuristic.html
echo   - AI Backend: http://localhost:3006
echo   - Blockchain: http://localhost:3007
echo   - Admin API: http://localhost:3008
echo   - SD AI Mock: http://localhost:8000
echo.
echo Logs are in the 'logs' directory
echo.
echo Press any key to exit...
pause >nul