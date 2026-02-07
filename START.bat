@echo off
echo ========================================
echo Todo Chatbot - Starting Services
echo ========================================
echo.

REM Check if OpenRouter API key is set
if "%OPENROUTER_API_KEY%"=="" (
    echo ERROR: OPENROUTER_API_KEY not set!
    echo.
    echo Please run this first:
    echo set OPENROUTER_API_KEY=sk-or-v1-your-key-here
    echo.
    echo Get your API key from: https://openrouter.ai/keys
    echo.
    pause
    exit /b 1
)

echo Step 1: Initializing Dapr (one-time setup)...
dapr init
if errorlevel 1 (
    echo Dapr init failed or already initialized
)

echo.
echo Step 2: Starting Backend API with Dapr...
echo Backend will run on http://localhost:8001
echo.

cd /d "%~dp0backend\src\services\chat-api"
start "Chat API Backend" cmd /k "dapr run --app-id chat-api --app-port 8001 --dapr-http-port 3500 -- python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Step 3: Starting WebSocket Sync Service with Dapr...
echo WebSocket will run on ws://localhost:8004/ws
echo.

cd /d "%~dp0backend\src\services\websocket_sync"
start "WebSocket Sync" cmd /k "dapr run --app-id websocket-sync --app-port 8004 --dapr-http-port 3504 -- python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload"

echo Waiting 5 seconds for WebSocket service to start...
timeout /t 5 /nobreak > nul

echo.
echo Step 4: Starting Frontend...
echo Frontend will run on http://localhost:3000
echo.

cd /d "%~dp0frontend"
start "Frontend" cmd /k "set NEXT_PUBLIC_API_URL=http://localhost:8001 && set NEXT_PUBLIC_WS_URL=ws://localhost:8004 && npm run dev"

echo.
echo ========================================
echo Services Started Successfully!
echo ========================================
echo.
echo Open your browser:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8001
echo   API Docs: http://localhost:8001/docs
echo   WebSocket: ws://localhost:8004/ws
echo.
echo Three terminal windows have opened:
echo   1. Chat API Backend (with Dapr)
echo   2. WebSocket Sync Service (with Dapr)
echo   3. Frontend (Next.js)
echo.
echo Close those windows to stop the services.
echo.
pause
