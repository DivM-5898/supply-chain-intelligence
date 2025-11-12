#!/bin/bash

# Supply Chain Intelligence Platform - Server Startup Script

echo "========================================"
echo "Supply Chain Intelligence Platform"
echo "Starting Backend and Frontend Servers"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r backend/requirements.txt
    echo "✅ Dependencies installed"
    echo ""
fi

# Kill any existing processes on ports 8000 and 8080
echo "Checking for existing processes..."
PORT_8000=$(lsof -ti:8000)
PORT_8080=$(lsof -ti:8080)

if [ ! -z "$PORT_8000" ]; then
    echo "   Killing process on port 8000 (PID: $PORT_8000)..."
    kill -9 $PORT_8000 2>/dev/null
    sleep 2
fi

if [ ! -z "$PORT_8080" ]; then
    echo "   Killing process on port 8080 (PID: $PORT_8080)..."
    kill -9 $PORT_8080 2>/dev/null
    sleep 2
fi

echo "✅ Ports cleared"
echo ""

# Start backend
echo "Starting Backend Server (Port 8000)..."
source venv/bin/activate
cd backend
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Logs: backend.log"
echo ""

# Wait for backend to be ready
echo "Waiting for backend to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/integrated/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend startup timeout (check backend.log)"
    fi
    sleep 1
done
echo ""

# Start frontend
echo "Starting Frontend Server (Port 8080)..."
cd frontend
nohup python server.py > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Logs: frontend.log"
echo ""

# Wait for frontend to be ready
echo "Waiting for frontend to initialize..."
for i in {1..10}; do
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠️  Frontend startup timeout (check frontend.log)"
    fi
    sleep 1
done
echo ""

# Save PIDs to file
echo "$BACKEND_PID" > .server_pids
echo "$FRONTEND_PID" >> .server_pids

echo "========================================"
echo "✅ All Servers Running!"
echo "========================================"
echo ""
echo "🌐 Access Points:"
echo "   Frontend: http://localhost:8080"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Process Information:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "📊 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop servers:"
echo "   ./stop_servers.sh"
echo "   OR: kill $BACKEND_PID $FRONTEND_PID"
echo "========================================"
echo ""
echo "🎉 Open your browser to http://localhost:8080"
echo ""
