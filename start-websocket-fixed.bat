@echo off
echo ========================================
echo Starting WebSocket Sync Service
echo ========================================
echo.

REM Navigate to backend/src directory (parent of services)
cd /d "%~dp0backend\src"

echo Starting WebSocket Sync Service...
echo.
echo Service will run on: ws://localhost:8004/ws
echo Health check: http://localhost:8004/
echo Stats: http://localhost:8004/stats
echo.
echo Press Ctrl+C to stop the service.
echo.

REM Run with uvicorn from the src directory
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004 --reload
