# WebSocket Service Startup Guide

## Quick Fix (Recommended)

**Just run this command:**
```cmd
QUICK_FIX_WEBSOCKET.bat
```

This will:
1. ✅ Check Python installation
2. ✅ Install required dependencies
3. ✅ Start the WebSocket service on port 8004

**Keep this terminal window open!** The WebSocket service needs to run continuously.

---

## What's Happening?

Your frontend is trying to connect to `ws://localhost:8004/ws` but the WebSocket Sync Service isn't running.

### Current Status
- ✅ Frontend: Running on port 3000
- ✅ Chat API: Running on port 8001
- ❌ **WebSocket Service: NOT RUNNING** ← This is the problem!

---

## Step-by-Step Manual Fix

### Step 1: Open a New Terminal
Don't close your existing terminals! Open a **new Command Prompt**.

### Step 2: Navigate to Project Directory
```cmd
cd "E:\Python.py\Hackaton 2(1)"
```

### Step 3: Install Dependencies (First Time Only)
```cmd
cd backend\src\services\websocket_sync
pip install -r requirements.txt
```

### Step 4: Start the WebSocket Service
```cmd
python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

### Step 5: Verify It's Running
Open a browser and go to: http://localhost:8004

You should see:
```json
{
  "service": "websocket-sync",
  "version": "1.0.0",
  "status": "running"
}
```

---

## Using the Updated START.bat

The `START.bat` script has been updated to start all 3 services automatically.

### Option A: Restart Everything (Clean Start)
1. **Close all running terminals** (Frontend, Chat API)
2. **Run START.bat**:
   ```cmd
   START.bat
   ```
3. **Wait for 3 terminal windows to open**:
   - Chat API Backend (port 8001)
   - WebSocket Sync Service (port 8004) ← NEW!
   - Frontend (port 3000)

### Option B: Just Start WebSocket (Keep Others Running)
If you want to keep your current services running:
```cmd
QUICK_FIX_WEBSOCKET.bat
```

---

## Verification Checklist

### 1. Check WebSocket Service is Running
```cmd
curl http://localhost:8004
```

**Expected Output:**
```json
{
  "service": "websocket-sync",
  "version": "1.0.0",
  "status": "running"
}
```

### 2. Check Service Stats
```cmd
curl http://localhost:8004/stats
```

**Expected Output:**
```json
{
  "connections": {
    "total": 0,
    "users": 0
  },
  "sequences": {...}
}
```

### 3. Check Frontend Connection
1. Open http://localhost:3000/chat
2. Open browser DevTools (F12)
3. Go to Console tab
4. Look for: `WebSocket connected` ✅
5. Check the status indicator in the top-right corner shows "Live" 🟢

---

## Troubleshooting

### Error: "Address already in use"
Port 8004 is already taken by another process.

**Solution:**
```cmd
# Find what's using port 8004
netstat -ano | findstr :8004

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F

# Then start the service again
QUICK_FIX_WEBSOCKET.bat
```

### Error: "ModuleNotFoundError: No module named 'fastapi'"
Dependencies not installed.

**Solution:**
```cmd
cd backend\src\services\websocket_sync
pip install -r requirements.txt
```

### Error: "ModuleNotFoundError: No module named 'connection_manager'"
Wrong directory or import issues.

**Solution:**
```cmd
# Make sure you're in the right directory
cd backend\src\services\websocket_sync

# Try running with Python module syntax
python -m uvicorn main:app --host 0.0.0.0 --port 8004
```

### Error: "Cannot import name 'ConnectionManager'"
Missing or incomplete service files.

**Solution:**
Check if these files exist:
- `backend/src/services/websocket_sync/connection_manager.py`
- `backend/src/services/websocket_sync/routes/websocket.py`
- `backend/src/services/websocket_sync/routes/health.py`
- `backend/src/services/websocket_sync/handlers/task_updates.py`
- `backend/src/services/websocket_sync/services/broadcaster.py`

### Frontend Still Shows "Connection Refused"
1. **Verify service is running**: Check http://localhost:8004
2. **Check frontend environment**: Make sure `NEXT_PUBLIC_WS_URL=ws://localhost:8004` is set
3. **Restart frontend**: Stop and restart the frontend to pick up new environment variables
4. **Clear browser cache**: Hard refresh (Ctrl+Shift+R)

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Frontend (Port 3000)            │
│                                         │
│  - Next.js Application                  │
│  - Chat Interface                       │
│  - Real-time Updates                    │
└────────────┬───────────────┬────────────┘
             │               │
             │ HTTP          │ WebSocket
             │               │
             ▼               ▼
┌─────────────────┐  ┌──────────────────┐
│   Chat API      │  │  WebSocket Sync  │
│  (Port 8001)    │  │   (Port 8004)    │
│                 │  │                  │
│  - REST API     │  │  - WS Server     │
│  - AI Chat      │  │  - Real-time     │
│  - Task CRUD    │  │  - Broadcasts    │
└─────────────────┘  └──────────────────┘
```

### What Each Service Does

**Chat API (Port 8001)**
- Handles HTTP REST API requests
- AI-powered chat interface
- Task CRUD operations
- Publishes events to Dapr (optional)

**WebSocket Sync (Port 8004)**
- Maintains WebSocket connections
- Broadcasts real-time updates
- Handles reconnection logic
- Syncs task changes across clients

**Frontend (Port 3000)**
- User interface
- Connects to both services:
  - HTTP → Chat API (8001)
  - WebSocket → WebSocket Sync (8004)

---

## Running with Dapr (Advanced)

If you want to use Dapr for event-driven features:

### Prerequisites
```cmd
# Install Dapr CLI
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Initialize Dapr
dapr init
```

### Start with Dapr
```cmd
cd backend\src\services\websocket_sync
dapr run --app-id websocket-sync --app-port 8004 --dapr-http-port 3504 -- python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

---

## Quick Reference

### Start All Services
```cmd
START.bat
```

### Start Just WebSocket
```cmd
QUICK_FIX_WEBSOCKET.bat
```

### Check Service Status
```cmd
# WebSocket
curl http://localhost:8004

# Chat API
curl http://localhost:8001/health

# Frontend
# Open http://localhost:3000
```

### Stop Services
Press `Ctrl+C` in each terminal window

---

## Next Steps

1. ✅ Run `QUICK_FIX_WEBSOCKET.bat`
2. ✅ Wait for "Application startup complete"
3. ✅ Open http://localhost:3000/chat
4. ✅ Check browser console - no more errors!
5. ✅ See "Live" indicator in top-right corner
6. ✅ Try creating a task and watch for real-time notifications

---

## Support

- **WebSocket not connecting?** Check this guide's Troubleshooting section
- **Missing dependencies?** Run `pip install -r requirements.txt`
- **Port conflicts?** Use `netstat -ano | findstr :8004` to find conflicts
- **Still stuck?** Check the terminal output for specific error messages

---

**Status**: Ready to fix! Just run `QUICK_FIX_WEBSOCKET.bat` 🚀
