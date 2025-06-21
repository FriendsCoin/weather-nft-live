@echo off
echo Installing ngrok via Winget...
winget install ngrok.ngrok

echo.
echo Checking if ngrok is installed...
ngrok version

echo.
echo If ngrok version shows, installation was successful!
echo You can now run: ngrok http 8000
pause