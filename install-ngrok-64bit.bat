@echo off
echo Installing ngrok 64-bit for Windows...

echo Creating ngrok directory...
mkdir C:\ngrok 2>NUL

echo Downloading ngrok 64-bit...
powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'C:\ngrok\ngrok.zip'"

echo Extracting ngrok...
powershell -Command "Expand-Archive -Path 'C:\ngrok\ngrok.zip' -DestinationPath 'C:\ngrok' -Force"

echo Cleaning up...
del C:\ngrok\ngrok.zip

echo Testing ngrok installation...
C:\ngrok\ngrok.exe version

echo.
echo ✅ Ngrok 64-bit installed successfully!
echo.
echo Usage:
echo C:\ngrok\ngrok.exe http 8000
echo.
echo To add to PATH permanently:
echo 1. Windows key + X → System
echo 2. Advanced system settings → Environment Variables
echo 3. System Variables → Path → Edit → New → C:\ngrok
echo 4. Restart PowerShell, then use: ngrok http 8000

pause