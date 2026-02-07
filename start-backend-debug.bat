@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Backend Startup - Comprehensive Check
echo ========================================
echo.

REM Step 1: Check OpenRouter API Key
echo [1/6] Checking OpenRouter API Key...
if "%OPENROUTER_API_KEY%"=="" (
    echo.
    echo ERROR: OPENROUTER_API_KEY not set!
    echo.
    echo You need to set your OpenRouter API key first.
    echo.
    echo Steps:
    echo   1. Get your key from: https://openrouter.ai/keys
    echo   2. In THIS window, run: set OPENROUTER_API_KEY=sk-or-v1-your-key
    echo   3. Then run this script again
    echo.
    pause
    exit /b 1
)
echo    ✓ API Key is set
echo.

REM Step 2: Check Python
echo [2/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo    ✗ Python not found!
    echo    Please install Python 3.11+ and add to PATH
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo    ✓ Found: !PYTHON_VERSION!
echo.

REM Step 3: Navigate to backend directory
echo [3/6] Navigating to backend directory...
cd /d "%~dp0backend\src"
if errorlevel 1 (
    echo    ✗ Failed to navigate to backend directory
    pause
    exit /b 1
)
echo    ✓ Current directory: %CD%
echo.

REM Step 4: Check if main.py exists
echo [4/6] Checking if main.py exists...
if not exist "services\chat-api\main.py" (
    echo    ✗ main.py not found at services\chat-api\main.py
    echo    Current directory: %CD%
    pause
    exit /b 1
)
echo    ✓ main.py found
echo.

REM Step 5: Set environment variables
echo [5/6] Setting environment variables...
set PYTHONPATH=%CD%;%PYTHONPATH%
set PORT=8001
set DAPR_HTTP_PORT=3500
set ENVIRONMENT=local-dev
set LOG_LEVEL=info
echo    ✓ PYTHONPATH=%CD%
echo    ✓ PORT=8001
echo.

REM Step 6: Start backend
echo [6/6] Starting backend server...
echo.
echo ========================================
echo Backend Starting
echo ========================================
echo.
echo Backend URL: http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

cd services\chat-api
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

endlocal
