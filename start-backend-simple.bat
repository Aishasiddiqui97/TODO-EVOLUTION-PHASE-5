@echo off
echo ========================================
echo Starting Backend Service (Simple Mode)
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
    pause
    exit /b 1
)

echo OpenRouter API Key: Set ✓
echo.

REM Navigate to backend src directory (where shared module is)
cd /d "%~dp0backend\src"

REM Add current directory to PYTHONPATH so Python can find 'shared' module
set PYTHONPATH=%CD%;%PYTHONPATH%

echo Starting Backend API (without Dapr - for testing)...
echo.
echo Backend will run on: http://localhost:8001
echo API Docs will be at: http://localhost:8001/docs
echo.
echo NOTE: This runs without Dapr, so:
echo   - Events won't be published
echo   - State won't persist between restarts
echo   - Good for testing the API
echo.
echo Press Ctrl+C to stop the backend.
echo.

REM Set environment variables
set PORT=8001
set DAPR_HTTP_PORT=3500
set ENVIRONMENT=local-dev
set LOG_LEVEL=info

REM Start backend directly with uvicorn from the services/chat-api directory
cd services\chat-api
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
