@echo off
echo ========================================
echo Phishing Detection Assistant - Setup
echo ========================================
echo.

echo Step 1: Installing Python dependencies...
pip install flask flask-cors pillow
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo Step 2: Creating extension icons...
python create-icons.py
if errorlevel 1 (
    echo Warning: Could not create icons automatically
    echo Please create icons manually or use an online generator
)
echo.

echo Step 3: Starting backend API...
echo Backend will run on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo Next steps:
echo 1. Keep this window open (backend running)
echo 2. Open Chrome/Edge and go to extensions page
echo 3. Enable Developer Mode
echo 4. Click "Load unpacked" and select this folder
echo 5. Test the extension on Gmail or Outlook
echo ========================================
echo.

python api-example.py
