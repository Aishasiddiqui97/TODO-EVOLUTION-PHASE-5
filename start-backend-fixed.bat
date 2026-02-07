@echo off
echo ========================================
echo Starting Backend - Simple Version
echo ========================================
echo.

REM Check API Key
if "%OPENROUTER_API_KEY%"=="" (
    echo ERROR: OPENROUTER_API_KEY not set!
    echo.
    echo Set it first: set OPENROUTER_API_KEY=sk-or-v1-your-key
    echo Get key from: https://openrouter.ai/keys
    echo.
    pause
    exit /b 1
)

echo Step 1: API Key is set ✓
echo.

REM Check Python
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo Step 2: Python found ✓
echo.

REM Navigate and set PYTHONPATH
echo Step 3: Setting up paths...
cd /d "%~dp0backend\src"
set PYTHONPATH=%~dp0backend\src
echo PYTHONPATH set to: %PYTHONPATH%
echo.

REM Set environment variables
echo Step 4: Setting environment variables...
set PORT=8001
set DAPR_HTTP_PORT=3500
set ENVIRONMENT=local-dev
set LOG_LEVEL=info
echo Environment configured ✓
echo.

REM Start server
echo Step 5: Starting backend server...
echo.
echo ========================================
echo Backend will run on: http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

cd services\chat-api
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
