@echo off
echo Fixing ngrok - installing 64-bit version...

echo Removing old ngrok installations...
rmdir /s /q C:\ngrok 2>NUL
del C:\Windows\System32\ngrok.exe 2>NUL
del C:\Windows\ngrok.exe 2>NUL

echo Creating fresh ngrok directory...
mkdir C:\ngrok

echo Downloading ngrok 64-bit from official source...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'C:\ngrok\ngrok-64bit.zip'}"

echo Extracting ngrok 64-bit...
powershell -Command "Expand-Archive -Path 'C:\ngrok\ngrok-64bit.zip' -DestinationPath 'C:\ngrok' -Force"

echo Cleaning up...
del C:\ngrok\ngrok-64bit.zip

echo Testing ngrok 64-bit installation...
echo.
C:\ngrok\ngrok.exe version
echo.

if %ERRORLEVEL% EQU 0 (
    echo ✅ Success! ngrok 64-bit installed correctly
    echo.
    echo Usage: C:\ngrok\ngrok.exe http 8000
    echo.
    echo To add to PATH:
    echo 1. Windows key + X → System → Advanced system settings
    echo 2. Environment Variables → System Variables → Path → Edit → New
    echo 3. Add: C:\ngrok
    echo 4. Restart PowerShell, then use: ngrok http 8000
) else (
    echo ❌ Installation failed. Try downloading manually from:
    echo https://ngrok.com/download
    echo Choose: Windows (64-bit)
)

pause