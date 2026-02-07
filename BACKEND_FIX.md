# 🔧 Backend Error Fix - Two Solutions

## Problem
Dapr CLI is installed but not found in PATH. This happens because Command Prompt needs to be restarted after Dapr installation.

---

## ✅ Solution 1: Simple Mode (Recommended for Quick Start)

**Use this to get started quickly without Dapr.**

### What You Get:
✅ Backend API works
✅ Chat interface works
✅ Task management works
✅ OpenRouter AI works

### What Doesn't Work:
❌ Event publishing (no other services running anyway)
❌ State persistence (tasks lost on restart)

### How to Run:

**Step 1:** Open Command Prompt and set your API key:
```cmd
cd E:\Python.py\Hackaton 2(1)
set OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Step 2:** Start backend in simple mode:
```cmd
start-backend-simple.bat
```

**Step 3:** Wait for this message:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Step 4:** Open a NEW Command Prompt and start frontend:
```cmd
cd E:\Python.py\Hackaton 2(1)
start-frontend.bat
```

**Step 5:** Open browser to: **http://localhost:3000**

---

## ✅ Solution 2: Full Mode with Dapr (All Features)

**Use this for full functionality with event-driven architecture.**

### What You Get:
✅ Everything from Simple Mode
✅ Event publishing
✅ State persistence
✅ Full Dapr features

### Prerequisites:
- Docker Desktop must be running
- Dapr must be initialized

### How to Run:

**Step 1:** Make sure Docker Desktop is running

**Step 2:** Open Command Prompt and set your API key:
```cmd
cd E:\Python.py\Hackaton 2(1)
set OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Step 3:** Start backend with Dapr:
```cmd
start-backend-with-dapr.bat
```

This will:
- Initialize Dapr (first time only, takes 2-3 minutes)
- Start Redis container
- Start Zipkin container
- Start backend with Dapr sidecar

**Step 4:** Wait for this message:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Step 5:** Open a NEW Command Prompt and start frontend:
```cmd
cd E:\Python.py\Hackaton 2(1)
start-frontend.bat
```

**Step 6:** Open browser to: **http://localhost:3000**

---

## 🎯 Which Should You Use?

### Use Simple Mode If:
- You just want to test the application quickly
- You don't have Docker Desktop
- You don't need state persistence
- You're just trying out the AI chat features

### Use Full Mode If:
- You want all features
- You have Docker Desktop running
- You want tasks to persist between restarts
- You're doing serious development

---

## 🧪 Test Backend is Working

After starting the backend (either mode), open a NEW Command Prompt and run:

```cmd
curl http://localhost:8001/health
```

Should return:
```json
{"status":"healthy","service":"chat-api",...}
```

---

## 🚨 Troubleshooting

### Simple Mode Issues

**"Python not found"**
```cmd
python --version
```
If this fails, Python isn't in PATH. Reinstall Python and check "Add to PATH".

**"Module not found"**
```cmd
cd E:\Python.py\Hackaton 2(1)\backend\src\services\chat-api
pip install -r requirements.txt
```

**"Port 8001 already in use"**
```cmd
netstat -ano | findstr :8001
taskkill /PID <process-id> /F
```

### Full Mode Issues

**"Docker not running"**
- Start Docker Desktop
- Wait for it to fully start (green icon in system tray)
- Try again

**"Dapr init fails"**
- Make sure Docker Desktop is running
- Check Docker is set to Linux containers (not Windows containers)
- Try: `C:\dapr\dapr.exe uninstall` then `C:\dapr\dapr.exe init`

**"Redis connection failed"**
- Run: `docker ps` to see if Redis container is running
- If not, run: `C:\dapr\dapr.exe init` again

---

## 📝 Summary

**Quick Start (Recommended):**
1. Set API key: `set OPENROUTER_API_KEY=sk-or-v1-...`
2. Run: `start-backend-simple.bat`
3. Wait for "Uvicorn running"
4. In new window, run: `start-frontend.bat`
5. Open: http://localhost:3000

**Full Features:**
1. Start Docker Desktop
2. Set API key: `set OPENROUTER_API_KEY=sk-or-v1-...`
3. Run: `start-backend-with-dapr.bat`
4. Wait for "Uvicorn running" (first time takes 2-3 minutes)
5. In new window, run: `start-frontend.bat`
6. Open: http://localhost:3000

---

**Choose one and let me know if you encounter any errors!**
