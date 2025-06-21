@echo off
echo Alternative ngrok setup - Manual download method

echo.
echo If automatic download fails, follow these steps:
echo.
echo 1. Open browser and go to: https://ngrok.com/download
echo 2. Click "Windows (64-bit)" - this downloads ngrok-v3-stable-windows-amd64.zip
echo 3. Extract the ZIP file
echo 4. Copy ngrok.exe to C:\ngrok\
echo 5. Test with: C:\ngrok\ngrok.exe version
echo.

echo Creating directory...
mkdir C:\ngrok 2>NUL

echo Opening download page...
start https://ngrok.com/download

echo.
echo After manual download:
echo 1. Extract ngrok.exe from ZIP
echo 2. Copy to C:\ngrok\
echo 3. Run: C:\ngrok\ngrok.exe version
echo 4. If working, use: C:\ngrok\ngrok.exe http 8000

pause