# Run on Localhost - Simple Manual Steps

## Step 1: Initialize Dapr (One-time setup)

Open Command Prompt and run:

```cmd
dapr init
```

Wait for it to complete (downloads Redis and Zipkin containers).

## Step 2: Install Backend Dependencies

```cmd
cd E:\Python.py\Hackaton 2(1)\backend\src\services\chat-api
pip install fastapi uvicorn openai dapr pydantic python-dotenv httpx
```

## Step 3: Install Frontend Dependencies

```cmd
cd E:\Python.py\Hackaton 2(1)\frontend
npm install
```

## Step 4: Set OpenRouter API Key

```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

**Get your API key from:** https://openrouter.ai/keys

**Optional - Choose a model:**
```cmd
set OPENROUTER_MODEL=openai/gpt-4-turbo-preview
```

Available models: https://openrouter.ai/models

## Step 5: Start Backend (Terminal 1)

Open a NEW Command Prompt window and run:

```cmd
cd E:\Python.py\Hackaton 2(1)\backend\src\services\chat-api
dapr run --app-id chat-api --app-port 8001 --dapr-http-port 3500 -- python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Step 6: Start Frontend (Terminal 2)

Open ANOTHER Command Prompt window and run:

```cmd
cd E:\Python.py\Hackaton 2(1)\frontend
set NEXT_PUBLIC_API_URL=http://localhost:8001
npm run dev
```

## Step 7: Access the Application

Open your browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/docs

## Troubleshooting

### If "dapr: command not found"
Close and reopen your Command Prompt (PATH needs to refresh after Dapr install).

### If Redis connection fails
Make sure Docker Desktop is running, then run `dapr init` again.

### If port 3000 or 8001 is busy
Find and kill the process:
```cmd
netstat -ano | findstr :3000
taskkill /PID <process-id> /F
```

## Quick Test

Once both services are running, test the API:

```cmd
curl http://localhost:8001/health
```

Should return: `{"status":"healthy","service":"chat-api",...}`
