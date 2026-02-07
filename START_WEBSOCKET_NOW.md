# 🚀 START WEBSOCKET SERVICE NOW!

## The Problem
Your frontend shows this error:
```
WebSocket connection to 'ws://localhost:8004/' failed: 
Error in connection establishment: net::ERR_CONNECTION_REFUSED
```

**This means the WebSocket Sync Service is NOT running on port 8004.**

---

## ✅ SOLUTION: Run This Command

### Open a NEW Command Prompt and run:

```cmd
start-websocket-fixed.bat
```

**That's it!** Keep this terminal window open.

---

## What This Does

The script will:
1. Navigate to the correct directory (`backend/src`)
2. Start the WebSocket service using Python's uvicorn server
3. Listen on port 8004 for WebSocket connections
4. Enable auto-reload for development

---

## Verify It's Working

### Step 1: Check the Terminal Output
You should see something like:
```
INFO:     Uvicorn running on http://0.0.0.0:8004 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Test the Service
Open a browser and go to: **http://localhost:8004**

You should see:
```json
{
  "service": "websocket-sync",
  "version": "1.0.0",
  "status": "running"
}
```

### Step 3: Check Your Frontend
1. Go to **http://localhost:3000/chat**
2. Open browser DevTools (Press F12)
3. Look at the Console tab
4. You should see: `WebSocket connected` ✅
5. The status indicator in the top-right should show **"Live"** 🟢

---

## Alternative: Manual Command

If the batch file doesn't work, run this manually:

```cmd
cd "E:\Python.py\Hackaton 2(1)\backend\src"
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004 --reload
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'services'"
**Solution:** Make sure you're in the `backend/src` directory:
```cmd
cd backend\src
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004
```

### "Address already in use"
**Solution:** Port 8004 is taken. Kill the process:
```cmd
netstat -ano | findstr :8004
taskkill /PID <PID_NUMBER> /F
```

### "ModuleNotFoundError: No module named 'fastapi'"
**Solution:** Install dependencies:
```cmd
pip install fastapi uvicorn websockets httpx python-dotenv
```

### Frontend Still Shows Error
1. **Hard refresh the browser**: Ctrl+Shift+R
2. **Check the WebSocket URL**: Should be `ws://localhost:8004`
3. **Restart the frontend**: Stop and start the frontend service
4. **Check browser console**: Look for specific error messages

---

## Complete Service Architecture

You need **3 services** running:

```
Terminal 1: Chat API Backend
Port: 8001
Command: (Already running from START.bat)

Terminal 2: WebSocket Sync Service  ← YOU NEED THIS!
Port: 8004
Command: start-websocket-fixed.bat

Terminal 3: Frontend
Port: 3000
Command: (Already running from START.bat)
```

---

## Quick Reference

### Start WebSocket Service
```cmd
start-websocket-fixed.bat
```

### Check if Running
```cmd
curl http://localhost:8004
```

### Check Stats
```cmd
curl http://localhost:8004/stats
```

### Stop Service
Press `Ctrl+C` in the terminal

---

## Why This Happens

The original `START.bat` script was only starting 2 services:
- ✅ Chat API (port 8001)
- ✅ Frontend (port 3000)
- ❌ WebSocket Sync (port 8004) ← **MISSING!**

The WebSocket service is a separate microservice that handles real-time synchronization. Without it, the frontend can't establish WebSocket connections.

---

## Next Steps

1. ✅ Run `start-websocket-fixed.bat` in a new terminal
2. ✅ Wait for "Application startup complete"
3. ✅ Verify at http://localhost:8004
4. ✅ Refresh your frontend at http://localhost:3000/chat
5. ✅ Check browser console - error should be gone!
6. ✅ See "Live" indicator in the chat interface

---

## Need Help?

If you're still having issues:

1. **Check all 3 services are running**:
   - Chat API: http://localhost:8001/health
   - WebSocket: http://localhost:8004
   - Frontend: http://localhost:3000

2. **Check the terminal outputs** for error messages

3. **Check browser console** (F12) for specific errors

4. **Try the manual command** instead of the batch file

---

**🎯 Bottom Line: Just run `start-websocket-fixed.bat` and keep it running!**
