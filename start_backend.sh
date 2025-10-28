#!/bin/bash

# Chronicle Backend Startup Script
# Starts backend and automatically warms up Ollama

cd "$(dirname "$0")"

echo "🚀 Starting Chronicle Backend..."

# Kill any existing backend
pkill -f "uvicorn backend.main:app" 2>/dev/null

# Start backend in background
backend/.venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "📋 Logs: tail -f backend.log"

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/ask/status > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    sleep 1
done

# Warm up Ollama in background
echo ""
echo "🔥 Warming up Ollama model (this takes ~60-90 seconds)..."
echo "   You can start using Chronicle now - first AI request will complete the warmup."
echo ""

curl -s -X POST http://localhost:8000/ask/warmup > /tmp/chronicle_warmup.log 2>&1 &

echo "📊 Backend running on: http://0.0.0.0:8000"
echo "🌐 Access Chronicle at: http://192.168.0.15:5173"
echo ""
echo "To stop: pkill -f 'uvicorn backend.main:app'"
