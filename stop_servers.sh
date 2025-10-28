#!/bin/bash

# Stop script for Chron application servers

echo "🛑 Stopping Chron application servers..."

# Function to stop processes on a specific port
stop_port() {
    local port=$1
    local service_name=$2
    
    echo "🔍 Looking for processes on port $port ($service_name)..."
    
    # Find PIDs using the port
    PIDS=$(lsof -ti:$port 2>/dev/null)
    
    if [ -z "$PIDS" ]; then
        echo "ℹ️  No processes found on port $port"
        return
    fi
    
    echo "🛑 Stopping $service_name processes: $PIDS"
    
    # Try graceful shutdown first
    kill $PIDS 2>/dev/null
    sleep 2
    
    # Check if processes are still running
    REMAINING=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$REMAINING" ]; then
        echo "💀 Force killing remaining processes: $REMAINING"
        kill -9 $REMAINING 2>/dev/null
    fi
    
    echo "✅ $service_name stopped"
}

# Stop backend (port 8000)
stop_port 8000 "Backend"

# Stop frontend (port 5173)
stop_port 5173 "Frontend"

# Also kill any remaining node or python processes that might be related
echo "🧹 Cleaning up any remaining processes..."
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "vite.*dev" 2>/dev/null || true

echo ""
echo "✅ All Chron application servers have been stopped"
echo ""

# Clean up log files if they exist
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$PROJECT_ROOT/backend.log" ]; then
    echo "📋 Backend log saved at: $PROJECT_ROOT/backend.log"
fi
if [ -f "$PROJECT_ROOT/frontend.log" ]; then
    echo "📋 Frontend log saved at: $PROJECT_ROOT/frontend.log"
fi