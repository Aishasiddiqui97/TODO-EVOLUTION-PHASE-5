# 🚀 How to Start the Application - Step by Step

## Problem: Backend Not Running

The error "localhost refused to connect" means the backend service isn't running yet.

---

## Solution: Start Backend and Frontend

### Step 1: Get OpenRouter API Key (If You Don't Have One)

1. Visit: **https://openrouter.ai/keys**
2. Sign up (free credits available)
3. Click "Create Key"
4. Copy your API key (starts with `sk-or-v1-`)

---

### Step 2: Open TWO Command Prompt Windows

You need 2 separate windows - one for backend, one for frontend.

**How to open Command Prompt:**
- Press `Windows Key + R`
- Type `cmd`
- Press Enter
- Repeat to open a second window

---

### Step 3: Start Backend (Terminal 1)

In the **first Command Prompt window**, run these commands:

```cmd
cd E:\Python.py\Hackaton 2(1)
set OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
start-backend.bat
```

**Replace `sk-or-v1-your-actual-key-here` with your real API key!**

**What you should see:**
```
Starting Backend API with Dapr...
Backend will run on: http://localhost:8001

== APP == INFO:     Started server process
== APP == INFO:     Waiting for application startup.
== APP == INFO:     Application startup complete.
== APP == INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Wait for this message before continuing!** It takes about 30 seconds.

---

### Step 4: Start Frontend (Terminal 2)

In the **second Command Prompt window**, run these commands:

```cmd
cd E:\Python.py\Hackaton 2(1)
start-frontend.bat
```

**What you should see:**
```
Starting Frontend on http://localhost:3000...

- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully
```

---

### Step 5: Open Your Browser

Once both services are running, open your browser and go to:

**http://localhost:3000**

You should see the Todo Chatbot interface!

---

## Quick Test

### Test Backend is Running

Open a **third Command Prompt** and run:

```cmd
curl http://localhost:8001/health
```

Should return:
```json
{"status":"healthy","service":"chat-api",...}
```

### Test Frontend is Running

Open your browser to: **http://localhost:3000**

You should see the chat interface.

---

## Troubleshooting

### "OPENROUTER_API_KEY not set"
- Make sure you set the key in the SAME window where you run start-backend.bat
- Don't close the window after setting the key
- Get your key from: https://openrouter.ai/keys

### "dapr: command not found"
- Close ALL Command Prompt windows
- Open a NEW Command Prompt (PATH needs to refresh)
- Try again

### "Port 8001 already in use"
Find and kill the process:
```cmd
netstat -ano | findstr :8001
taskkill /PID <process-id> /F
```

### "Port 3000 already in use"
Find and kill the process:
```cmd
netstat -ano | findstr :3000
taskkill /PID <process-id> /F
```

### Backend starts but shows errors
Check if Docker Desktop is running (Dapr needs it for Redis).

### Frontend can't connect to backend
- Make sure backend is fully started (wait for "Uvicorn running" message)
- Check backend is accessible: `curl http://localhost:8001/health`
- Make sure you're using http://localhost:3000 (not https)

---

## Alternative: Use the Original START.bat

If you want both services to start automatically in separate windows:

```cmd
cd E:\Python.py\Hackaton 2(1)
set OPENROUTER_API_KEY=sk-or-v1-your-key-here
START.bat
```

This will open 2 windows automatically (backend and frontend).

---

## What Each Service Does

### Backend (Port 8001)
- Handles AI chat requests
- Manages tasks (create, update, delete)
- Connects to OpenRouter API
- Uses Dapr for state management

### Frontend (Port 3000)
- User interface
- Chat interface
- Task display
- Connects to backend API

---

## Summary

**To fix "localhost refused to connect":**

1. Open 2 Command Prompt windows
2. In window 1: Set API key and run `start-backend.bat`
3. Wait 30 seconds for backend to start
4. In window 2: Run `start-frontend.bat`
5. Open browser to http://localhost:3000

**Both services must be running for the application to work!**

---

**Need help?** Check the error messages in the terminal windows for clues.
