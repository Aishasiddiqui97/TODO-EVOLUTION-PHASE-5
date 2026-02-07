@echo off
echo ========================================
echo QUICK FIX: Start WebSocket Service
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.12 or higher.
    pause
    exit /b 1
)

echo [1/3] Python found: 
python --version
echo.

REM Install dependencies
echo [2/3] Installing WebSocket service dependencies...
cd /d "%~dp0backend\src\services\websocket_sync"
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo WARNING: Some packages may have failed to install
    echo Trying to continue anyway...
)
echo Dependencies installed!
echo.

REM Start service
echo [3/3] Starting WebSocket Sync Service...
echo.
echo Service will run on: ws://localhost:8004/ws
echo Health check: http://localhost:8004/
echo Stats: http://localhost:8004/stats
echo.
echo Press Ctrl+C to stop the service.
echo.
echo ========================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
