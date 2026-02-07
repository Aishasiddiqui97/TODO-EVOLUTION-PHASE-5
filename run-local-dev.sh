#!/bin/bash

# Simple Local Development Setup
# Runs Chat API and Frontend directly on localhost (no Kubernetes)

set -e

echo "🚀 Starting Event-Driven Todo Chatbot (Local Dev Mode)"
echo "======================================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js"
    exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set!"
    echo "Please set it: export OPENAI_API_KEY='your-key-here'"
    echo ""
    read -p "Enter your OpenAI API key: " api_key
    export OPENAI_API_KEY="$api_key"
fi

echo "✅ Prerequisites OK"
echo ""

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend/src/services/chat-api
pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn openai dapr-ext-grpc pydantic python-dotenv

echo ""
echo "📦 Installing frontend dependencies..."
cd ../../../../frontend
npm install

echo ""
echo "✅ Dependencies installed"
echo ""

# Start backend in background
echo "🔧 Starting Chat API on http://localhost:8001..."
cd ../backend/src/services/chat-api
export PORT=8001
export ENVIRONMENT=local-dev
export LOG_LEVEL=info
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "🔧 Starting Frontend on http://localhost:3000..."
cd ../../../../frontend
export NEXT_PUBLIC_API_URL=http://localhost:8001
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8001"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
