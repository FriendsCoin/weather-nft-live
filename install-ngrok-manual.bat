@echo off
echo Downloading ngrok manually...

echo Creating ngrok directory...
mkdir C:\ngrok 2>NUL

echo Downloading ngrok.exe...
curl -L -o C:\ngrok\ngrok.exe https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.exe

echo Adding ngrok to PATH for current session...
set PATH=%PATH%;C:\ngrok

echo Testing ngrok installation...
C:\ngrok\ngrok.exe version

echo.
echo Ngrok installed! You can now use:
echo C:\ngrok\ngrok.exe http 8000
echo.
echo To add to PATH permanently:
echo 1. Windows key + R → sysdm.cpl
echo 2. Advanced → Environment Variables
echo 3. System Variables → Path → Edit → New → C:\ngrok
echo 4. Restart PowerShell

pause