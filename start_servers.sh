#!/bin/bash

# Launch script for Chron application
# Designed for Linux machine (192.168.0.15) accessed from Mac (192.168.0.12)

echo "🚀 Starting Chron application servers..."

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        return 0
    else
        return 1
    fi
}

# Function to start backend
start_backend() {
    echo "📦 Starting backend server on 0.0.0.0:8000..."
    
    # Check if virtual environment exists in backend directory
    if [ ! -d "$BACKEND_DIR/.venv" ]; then
        echo "❌ Virtual environment not found at $BACKEND_DIR/.venv"
        exit 1
    fi
    
    # Change to project root directory (so backend. imports work)
    cd "$PROJECT_ROOT"
    
    # Check if uvicorn is installed in the virtual environment
    if ! backend/.venv/bin/python -c "import uvicorn" 2>/dev/null; then
        echo "📥 Installing backend dependencies in virtual environment..."
        backend/.venv/bin/pip install -r backend/requirements.txt
    fi
    
    # Start backend server in background using virtual environment Python
    nohup backend/.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✅ Backend server started (PID: $BACKEND_PID)"
    echo "📋 Backend logs: $PROJECT_ROOT/backend.log"
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting frontend development server on 0.0.0.0:5173..."
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "📥 Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend server in background
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ Frontend server started (PID: $FRONTEND_PID)"
    echo "📋 Frontend logs: $PROJECT_ROOT/frontend.log"
}

# Main execution
echo "🔍 Checking ports..."
if check_port 8000; then
    echo "❌ Backend port 8000 is in use. Please stop the existing service first."
    exit 1
fi

if check_port 5173; then
    echo "❌ Frontend port 5173 is in use. Please stop the existing service first."
    exit 1
fi

# Start services
start_backend
sleep 2  # Give backend time to start
start_frontend

echo ""
echo "🎉 Chron application is starting up!"
echo ""
echo "📍 Access URLs:"
echo "   🖥️  Frontend (from Mac): http://192.168.0.15:5173"
echo "   🔌 Backend API (from Mac): http://192.168.0.15:8000"
echo "   📚 API Docs: http://192.168.0.15:8000/docs"
echo ""
echo "📋 Log files:"
echo "   📦 Backend: $PROJECT_ROOT/backend.log"
echo "   🎨 Frontend: $PROJECT_ROOT/frontend.log"
echo ""
echo "🛑 To stop the servers, run: ./stop_servers.sh"
echo ""
echo "⏳ Waiting a few seconds for services to fully start..."
sleep 5

# Check if services are responding
echo "🔍 Checking service health..."
if curl -s http://192.168.0.15:8000/docs > /dev/null; then
    echo "✅ Backend is responding"
else
    echo "⚠️  Backend may still be starting up"
fi

if curl -s http://192.168.0.15:5173 > /dev/null; then
    echo "✅ Frontend is responding"
else
    echo "⚠️  Frontend may still be starting up"
fi

echo ""
echo "🚀 Setup complete! You can now access the application from your Mac at:"
echo "   http://192.168.0.15:5173"