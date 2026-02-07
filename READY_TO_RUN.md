# 🚀 READY TO RUN - Final Steps

## Your System is Now Configured!

✅ Dapr CLI installed
✅ Backend dependencies installed
✅ Frontend dependencies installed
✅ Startup script created
✅ **Configured for OpenRouter** (access to multiple LLM models)

## Run the Application (3 Simple Steps)

### Step 1: Set Your OpenRouter API Key

Open Command Prompt and run:

```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

**Get your API key from:** https://openrouter.ai/keys

**Optional:** Set a specific model (defaults to GPT-4 Turbo):
```cmd
set OPENROUTER_MODEL=openai/gpt-4-turbo-preview
```

**Available models:**
- `openai/gpt-4-turbo-preview` (default, best quality)
- `openai/gpt-3.5-turbo` (faster, cheaper)
- `anthropic/claude-3-opus` (excellent reasoning)
- `anthropic/claude-3-sonnet` (balanced)
- `google/gemini-pro` (Google's model)
- `meta-llama/llama-3-70b-instruct` (open source)

See all models: https://openrouter.ai/models

### Step 2: Run the Startup Script

In the same Command Prompt window, run:

```cmd
cd E:\Python.py\Hackaton 2(1)
START.bat
```

This will:
- Initialize Dapr (first time only, takes ~2 minutes)
- Start the Backend API on port 8001
- Start the Frontend on port 3000
- Open 2 terminal windows (one for backend, one for frontend)

### Step 3: Open Your Browser

Once both services are running (wait ~30 seconds), open:

**Frontend:** http://localhost:3000

**Backend API Docs:** http://localhost:8001/docs

## What You'll See

### Terminal Window 1 (Backend)
```
== APP == INFO:     Started server process
== APP == INFO:     Waiting for application startup.
== APP == INFO:     Application startup complete.
== APP == INFO:     Uvicorn running on http://0.0

.0.0:8001
```

### Terminal Window 2 (Frontend)
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully
```

## Test the Application

### 1. Health Check
Open http://localhost:8001/health in your browser

Should show:
```json
{
  "status": "healthy",
  "service": "chat-api",
  "timestamp": "..."
}
```

### 2. Try the Chat Interface
1. Go to http://localhost:3000
2. Type: "Create a task to review proposal by Friday"
3. The AI will create the task for you!

### 3. View API Documentation
Go to http://localhost:8001/docs to see all available endpoints

## Troubleshooting

### "OPENROUTER_API_KEY not set"
Make sure you set the environment variable in the SAME Command Prompt window before running START.bat

Get your key from: https://openrouter.ai/keys

### "dapr: command not found"
Close and reopen Command Prompt (PATH needs to refresh)

### "Port 3000 already in use"
Kill the process:
```cmd
netstat -ano | findstr :3000
taskkill /PID <process-id> /F
```

### Backend won't start
Check if Docker Desktop is running (Dapr needs it for Redis)

### Frontend shows connection error
Wait 30 seconds for backend to fully start, then refresh the page

## Stop the Application

Close both terminal windows that were opened, or press Ctrl+C in each window.

## Next Steps

Once you verify it works:
1. Try creating tasks via chat
2. Test the REST API endpoints
3. Check the API documentation
4. Explore the features!

---

**You're all set!** Just run the 3 steps above and you'll have the application running on localhost.
