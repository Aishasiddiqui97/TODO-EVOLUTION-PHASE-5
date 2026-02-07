@echo off
echo ========================================
echo Starting Backend with Dapr (Full Path)
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

REM Check if Dapr exists using full path
if not exist "C:\dapr\dapr.exe" (
    echo ERROR: Dapr not found at C:\dapr\dapr.exe
    echo.
    echo Please run Dapr installation first.
    echo Or use start-backend-simple.bat to run without Dapr.
    pause
    exit /b 1
)

echo Dapr CLI: Found ✓
echo.

REM Initialize Dapr if needed
echo Initializing Dapr (if not already done)...
C:\dapr\dapr.exe init
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

REM Start backend with Dapr using full path
C:\dapr\dapr.exe run --app-id chat-api --app-port 8001 --dapr-http-port 3500 -- python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
