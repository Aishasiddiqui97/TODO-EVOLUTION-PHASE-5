@echo off
echo ========================================
echo Starting Todo Chatbot - Local Dev Mode
echo ========================================
echo.

REM Check prerequisites
where dapr >nul 2>nul
if errorlevel 1 (
    echo ERROR: Dapr CLI not found!
    echo Please install: https://docs.dapr.io/getting-started/install-dapr-cli/
    pause
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo ERROR: npm not found!
    pause
    exit /b 1
)

REM Check for OpenAI API key
if "%OPENAI_API_KEY%"=="" (
    echo WARNING: OPENAI_API_KEY not set!
    echo.
    set /p OPENAI_API_KEY="Enter your OpenAI API key: "
)

echo.
echo Initializing Dapr (local mode)...
dapr init
if errorlevel 1 (
    echo Dapr already initialized or failed
)

echo.
echo Installing backend dependencies...
cd backend\src\services\chat-api
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo Installing frontend dependencies...
cd ..\..\..\..\frontend
call npm install
if errorlevel 1 (
    echo Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting services...
echo ========================================
echo.

REM Create components directory for local Dapr
if not exist "%USERPROFILE%\.dapr\components" mkdir "%USERPROFILE%\.dapr\components"

REM Create local pubsub component
echo Creating local Dapr components...
(
echo apiVersion: dapr.io/v1alpha1
echo kind: Component
echo metadata:
echo   name: pubsub
echo spec:
echo   type: pubsub.redis
echo   version: v1
echo   metadata:
echo   - name: redisHost
echo     value: localhost:6379
echo   - name: redisPassword
echo     value: ""
) > "%USERPROFILE%\.dapr\components\pubsub.yaml"

REM Create local state store component
(
echo apiVersion: dapr.io/v1alpha1
echo kind: Component
echo metadata:
echo   name: statestore
echo spec:
echo   type: state.redis
echo   version: v1
echo   metadata:
echo   - name: redisHost
echo     value: localhost:6379
echo   - name: redisPassword
echo     value: ""
) > "%USERPROFILE%\.dapr\components\statestore.yaml"

echo.
echo Starting Backend with Dapr on http://localhost:8001...
cd /d "%~dp0backend\src\services\chat-api"
start "Chat API Backend" cmd /k "dapr run --app-id chat-api --app-port 8001 --dapr-http-port 3500 --components-path %USERPROFILE%\.dapr\components -- python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 10 /nobreak > nul

echo.
echo Starting Frontend on http://localhost:3000...
cd /d "%~dp0frontend"
start "Frontend" cmd /k "set NEXT_PUBLIC_API_URL=http://localhost:8001 && npm run dev"

echo.
echo ========================================
echo Services Started!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo Dapr Dashboard: http://localhost:8080
echo.
echo To view Dapr dashboard, run: dapr dashboard
echo.
echo Close the terminal windows to stop services
echo.
pause
