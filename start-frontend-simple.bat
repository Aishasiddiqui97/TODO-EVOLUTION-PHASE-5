@echo off
echo ========================================
echo Starting Frontend (Simple Mode)
echo ========================================
echo.

REM Navigate to frontend directory
cd /d "%~dp0frontend"

echo Installing dependencies (if needed)...
call npm install --silent
echo.

echo Starting Frontend on http://localhost:3000...
echo.
echo NOTE: WebSocket sync is disabled in simple mode.
echo       Real-time updates won't work, but chat and tasks will.
echo.
echo Press Ctrl+C to stop the frontend.
echo.

REM Disable WebSocket in simple mode
set NEXT_PUBLIC_API_URL=http://localhost:8001
set NEXT_PUBLIC_DISABLE_WEBSOCKET=true
npm run dev
