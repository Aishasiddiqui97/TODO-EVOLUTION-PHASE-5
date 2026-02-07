# Quick Start - Run on Localhost (Windows)

## Prerequisites

Before running, make sure you have:

1. **Python 3.11+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **Dapr CLI** - [Install Guide](https://docs.dapr.io/getting-started/install-dapr-cli/)
4. **OpenRouter API Key** - [Get one here](https://openrouter.ai/keys)

### Install Dapr CLI (Windows)

```powershell
# Run in PowerShell as Administrator
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

## Running the Application

### Step 1: Set OpenRouter API Key

```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

**Optional - Choose a specific model:**
```cmd
set OPENROUTER_MODEL=openai/gpt-4-turbo-preview
```

**Popular models:**
- `openai/gpt-4-turbo-preview` (default, best quality)
- `openai/gpt-3.5-turbo` (faster, cheaper)
- `anthropic/claude-3-opus` (excellent reasoning)
- `anthropic/claude-3-sonnet` (balanced)
- `google/gemini-pro` (Google's model)

See all models: https://openrouter.ai/models

### Step 2: Run the Application

Simply double-click `run-local-dev.bat` or run from command prompt:

```cmd
run-local-dev.bat
```

This will:
- Initialize Dapr (local mode with Redis)
- Install all dependencies
- Start the backend API on port 8001
- Start the frontend on port 3000

### Step 3: Access the Application

Once started, open your browser:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## What Gets Started

The script opens 2 terminal windows:

1. **Chat API Backend** - FastAPI server with Dapr sidecar
2. **Frontend** - Next.js development server

## Troubleshooting

### "Dapr CLI not found"
Install Dapr CLI using the command above, then restart your terminal.

### "Redis connection failed"
Run `dapr init` manually to set up local Redis:
```cmd
dapr init
```

### "Port already in use"
Kill processes using ports 3000 or 8001:
```cmd
netstat -ano | findstr :3000
netstat -ano | findstr :8001
taskkill /PID <process-id> /F
```

### Backend won't start
Check if all dependencies are installed:
```cmd
cd backend\src\services\chat-api
pip install -r requirements.txt
```

### Frontend won't start
Check if npm dependencies are installed:
```cmd
cd frontend
npm install
```

## Stopping the Application

Close both terminal windows that were opened by the script.

Or run:
```cmd
dapr stop --app-id chat-api
```

## Testing the API

### Create a Task
```bash
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Test Task\",\"userId\":\"user-001\",\"priority\":\"high\"}"
```

### Chat with AI
```bash
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Create a task to review proposal by Friday\",\"userId\":\"user-001\"}"
```

### List Tasks
```bash
curl http://localhost:8001/api/v1/tasks?userId=user-001
```

## Features Available in Local Mode

✅ Natural language task management
✅ AI-powered chat interface
✅ Task CRUD operations
✅ Search and filtering
✅ User preferences
✅ Event publishing (local Redis)
✅ State management (local Redis)

## What's NOT Available in Local Mode

❌ Recurring tasks (requires recurring-task service)
❌ Notifications (requires notification service)
❌ Real-time sync (requires websocket-sync service)
❌ Audit logs (requires audit-log service)

To run all services, use the full Kubernetes deployment.

## Next Steps

Once you verify the basic setup works:
1. Test the chat interface at http://localhost:3000
2. Try creating tasks via natural language
3. Check the API docs at http://localhost:8001/docs
4. View Dapr dashboard: `dapr dashboard`

For full production deployment with all services, see `DEPLOYMENT_COMMANDS.md`.
