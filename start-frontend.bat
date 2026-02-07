@echo off
echo ========================================
echo Starting Frontend Service
echo ========================================
echo.

REM Navigate to frontend directory
cd /d "%~dp0frontend"

echo Installing dependencies (if needed)...
call npm install --silent
echo.

echo Starting Frontend on http://localhost:3000...
echo.
echo Press Ctrl+C to stop the frontend.
echo.

REM Set API URL and start frontend
set NEXT_PUBLIC_API_URL=http://localhost:8001
npm run dev
