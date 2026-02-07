@echo off
echo ========================================
echo Starting WebSocket Sync Service
echo ========================================
echo.

REM Navigate to websocket service directory
cd /d "%~dp0backend\src\services\websocket_sync"

echo Starting WebSocket Sync Service with Dapr...
echo.
echo WebSocket will run on: ws://localhost:8004/ws
echo.
echo Press Ctrl+C to stop the service.
echo.

REM Start WebSocket service with Dapr
dapr run --app-id websocket-sync --app-port 8004 --dapr-http-port 3504 -- python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
