@echo off
echo ============================================
echo   PHISHING DETECTION ASSISTANT
echo   Starting Backend Server
echo ============================================
echo.

cd backend
echo Starting Flask API on http://localhost:5000...
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
