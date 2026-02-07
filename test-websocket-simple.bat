@echo off
echo ========================================
echo Testing WebSocket Service (Simple Mode)
echo ========================================
echo.
echo This will start the WebSocket service WITHOUT Dapr
echo to test if the basic service works.
echo.

cd /d "%~dp0backend\src\services\websocket_sync"

echo Starting WebSocket service on port 8004...
echo.
echo If you see "Application startup complete", the service is working!
echo Then press Ctrl+C and use start-websocket.bat instead.
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
