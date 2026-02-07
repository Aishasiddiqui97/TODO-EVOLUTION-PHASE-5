@echo off
echo ========================================
echo Starting Backend Service
echo ========================================
echo.

REM Check if OpenRouter API key is set
if "%OPENROUTER_API_KEY%"=="" (
    echo ERROR: OPENROUTER_API_KEY not set!
    echo.
    echo Please set it first:
    echo   set OPENROUTER_API_KEY=sk-or-v1-your-key-here
    echo.
    echo Get your API key from: https://openrouter.ai/keys
    echo.
    echo After setting the key, run this script again.
    pause
    exit /b 1
)

echo OpenRouter API Key: Set ✓
echo.

REM Check if Dapr is initialized
echo Checking Dapr...
dapr --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Dapr CLI not found!
    echo Please close and reopen Command Prompt to refresh PATH.
    pause
    exit /b 1
)

echo Dapr CLI: Found ✓
echo.

REM Initialize Dapr if needed
echo Initializing Dapr (if not already done)...
dapr init
echo.

REM Navigate to backend directory
cd /d "%~dp0backend\src\services\chat-api"

echo Starting Backend API with Dapr...
echo.
echo Backend will run on: http://localhost:8001
echo API Docs will be at: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the backend.
echo.

REM Start backend with Dapr
dapr run --app-id chat-api --app-port 8001 --dapr-http-port 3500 -- python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
