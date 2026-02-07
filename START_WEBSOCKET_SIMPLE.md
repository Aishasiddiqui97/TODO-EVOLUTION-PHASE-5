# Start WebSocket Backend - SIMPLE GUIDE

## 🎯 Just Run This Command

Open Command Prompt and run:

```cmd
start-websocket-fixed.bat
```

**That's it!** Keep the window open.

---

## 📋 Step-by-Step (If You Need It)

### Step 1: Open Command Prompt
- Press `Win + R`
- Type: `cmd`
- Press Enter

### Step 2: Go to Your Project
```cmd
cd "E:\Python.py\Hackaton 2(1)"
```

### Step 3: Run the Script
```cmd
start-websocket-fixed.bat
```

### Step 4: Wait for This Message
```
INFO:     Application startup complete.
```

### Step 5: Test It
Open browser: http://localhost:8004

Should show:
```json
{"service": "websocket-sync", "version": "1.0.0", "status": "running"}
```

---

## ✅ Success Indicators

### In Terminal
- ✅ `Uvicorn running on http://0.0.0.0:8004`
- ✅ `Application startup complete`

### In Browser (http://localhost:3000/chat)
- ✅ Red banner disappears
- ✅ Status shows "Live" (green)
- ✅ Console shows "WebSocket connected"

---

## 🔧 If It Doesn't Work

### Try Manual Command
```cmd
cd backend\src
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004
```

### Install Dependencies
```cmd
pip install fastapi uvicorn websockets httpx python-dotenv
```

### Check Port
```cmd
netstat -ano | findstr :8004
```

---

## 📝 What This Does

Starts the WebSocket Sync Service that provides:
- Real-time task updates
- Live synchronization across browser tabs
- WebSocket connections for the frontend

---

## 🎉 After It's Running

1. ✅ Keep the terminal open
2. ✅ Refresh your browser (http://localhost:3000/chat)
3. ✅ See "Live" status indicator
4. ✅ Enjoy real-time chat!

---

**Bottom Line:** Run `start-websocket-fixed.bat` and keep it running! 🚀
