# 🚀 Run WebSocket Backend Service

## Quick Start - Choose Your Method

### Method 1: Batch File (Recommended for Windows CMD)
```cmd
start-websocket-fixed.bat
```

### Method 2: PowerShell Script
```powershell
.\start-websocket.ps1
```

### Method 3: Manual Command
```cmd
cd backend\src
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004 --reload
```

---

## Step-by-Step Instructions

### For Command Prompt (CMD)

1. **Open Command Prompt**
   - Press `Win + R`
   - Type `cmd`
   - Press Enter

2. **Navigate to Project Directory**
   ```cmd
   cd "E:\Python.py\Hackaton 2(1)"
   ```

3. **Run the Batch File**
   ```cmd
   start-websocket-fixed.bat
   ```

4. **Wait for Success Message**
   ```
   INFO:     Application startup complete.
   ```

### For PowerShell

1. **Open PowerShell**
   - Press `Win + X`
   - Select "Windows PowerShell"

2. **Navigate to Project Directory**
   ```powershell
   cd "E:\Python.py\Hackaton 2(1)"
   ```

3. **Run the PowerShell Script**
   ```powershell
   .\start-websocket.ps1
   ```

4. **Wait for Success Message**
   ```
   INFO:     Application startup complete.
   ```

---

## What You Should See

### Terminal Output
```
========================================
Starting WebSocket Sync Service
========================================

Starting WebSocket service on port 8004...

Service URLs:
  WebSocket: ws://localhost:8004/ws
  Health:    http://localhost:8004/
  Stats:     http://localhost:8004/stats

Press Ctrl+C to stop the service

INFO:     Will watch for changes in these directories: ['E:\\Python.py\\Hackaton 2(1)\\backend\\src']
INFO:     Uvicorn running on http://0.0.0.0:8004 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Starting WebSocket Sync Service...
INFO:     WebSocket Sync Service started successfully
INFO:     Application startup complete.
```

---

## Verify It's Working

### Test 1: Check Service Status
Open browser and go to: **http://localhost:8004**

**Expected Response:**
```json
{
  "service": "websocket-sync",
  "version": "1.0.0",
  "status": "running"
}
```

### Test 2: Check Service Stats
Open browser and go to: **http://localhost:8004/stats**

**Expected Response:**
```json
{
  "connections": {
    "total": 0,
    "users": 0
  },
  "sequences": {
    "total_events": 0,
    "users_tracked": 0
  }
}
```

### Test 3: Check Frontend Connection
1. Open **http://localhost:3000/chat**
2. Press **F12** to open DevTools
3. Go to **Console** tab
4. Look for: `[WebSocket] Attempting to connect to: ws://localhost:8004/...`
5. Should see: `WebSocket connected` ✅

### Test 4: Check Status Indicator
Look at the top-right corner of the chat page:
- Should show: **"Live" 🟢** (green)
- Red banner should disappear

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'services'"

**Problem:** Running from wrong directory

**Solution:**
```cmd
cd backend\src
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004
```

### Error: "Address already in use"

**Problem:** Port 8004 is already taken

**Solution:**
```cmd
# Find what's using port 8004
netstat -ano | findstr :8004

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Try starting again
start-websocket-fixed.bat
```

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Problem:** Missing dependencies

**Solution:**
```cmd
cd backend\src\services\websocket_sync
pip install -r requirements.txt
```

### Error: "python: command not found"

**Problem:** Python not in PATH

**Solution:**
```cmd
# Use full path to Python
C:\Users\hp\AppData\Local\Programs\Python\Python312\python.exe -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004
```

### Service Starts But Frontend Still Shows Error

**Solution:**
1. **Hard refresh browser:** Ctrl+Shift+R
2. **Check WebSocket URL:** Should be `ws://localhost:8004`
3. **Check service is running:** Open http://localhost:8004
4. **Wait 5 seconds:** Give it time to reconnect
5. **Check browser console:** Look for specific errors

---

## Running All Services Together

You need **3 services** running for the full application:

### Terminal 1: Chat API Backend
```cmd
cd backend\src\services\chat_api
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Terminal 2: WebSocket Sync Service ← THIS ONE!
```cmd
cd backend\src
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004 --reload
```

### Terminal 3: Frontend
```cmd
cd frontend
npm run dev
```

---

## Using the Updated START.bat

The `START.bat` script has been updated to start all 3 services automatically:

```cmd
START.bat
```

This will open 3 terminal windows:
1. Chat API Backend (port 8001)
2. WebSocket Sync Service (port 8004) ← Includes this now!
3. Frontend (port 3000)

---

## Service Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Port 3000)            │
│         npm run dev                     │
└────────────┬───────────────┬────────────┘
             │               │
             │ HTTP          │ WebSocket
             │               │
             ▼               ▼
┌─────────────────┐  ┌──────────────────┐
│   Chat API      │  │  WebSocket Sync  │
│  (Port 8001)    │  │   (Port 8004)    │ ← YOU'RE STARTING THIS!
│                 │  │                  │
│  uvicorn        │  │  uvicorn         │
│  main:app       │  │  services.       │
│                 │  │  websocket_sync. │
│                 │  │  main:app        │
└─────────────────┘  └──────────────────┘
```

---

## Quick Reference

### Start Service
```cmd
start-websocket-fixed.bat
```

### Check if Running
```cmd
curl http://localhost:8004
```

### Check Logs
Look at the terminal where you started the service

### Stop Service
Press `Ctrl+C` in the terminal

### Restart Service
1. Press `Ctrl+C` to stop
2. Run `start-websocket-fixed.bat` again

---

## Environment Variables

The WebSocket service uses these environment variables (optional):

```bash
# WebSocket service port (default: 8004)
WS_PORT=8004

# Dapr HTTP port (default: 3500)
DAPR_HTTP_PORT=3500

# Log level (default: INFO)
LOG_LEVEL=INFO
```

---

## Development Tips

### Auto-Reload
The `--reload` flag enables auto-reload when you change code:
```cmd
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004 --reload
```

### Debug Mode
For more verbose logging:
```cmd
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004 --reload --log-level debug
```

### Without Reload (Production-like)
```cmd
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004
```

---

## Next Steps

1. ✅ Run `start-websocket-fixed.bat`
2. ✅ Wait for "Application startup complete"
3. ✅ Verify at http://localhost:8004
4. ✅ Refresh frontend at http://localhost:3000/chat
5. ✅ Check status indicator shows "Live" 🟢
6. ✅ Start chatting with real-time sync!

---

## Summary

### Command to Run
```cmd
start-websocket-fixed.bat
```

### What It Does
- Navigates to `backend/src`
- Starts WebSocket service on port 8004
- Enables auto-reload for development
- Provides real-time task synchronization

### Expected Result
- ✅ Service running on http://localhost:8004
- ✅ WebSocket endpoint at ws://localhost:8004/ws
- ✅ Frontend connects successfully
- ✅ Real-time updates work
- ✅ "Live" status indicator

**Now run the command and enjoy real-time chat!** 🚀
