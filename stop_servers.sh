#!/bin/bash

# Supply Chain Intelligence Platform - Server Stop Script

echo "========================================"
echo "Stopping Supply Chain Intelligence Platform"
echo "========================================"
echo ""

# Try to read PIDs from file
if [ -f ".server_pids" ]; then
    echo "Reading saved PIDs..."
    BACKEND_PID=$(sed -n '1p' .server_pids)
    FRONTEND_PID=$(sed -n '2p' .server_pids)
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null && echo "✅ Backend stopped" || echo "⚠️  Backend process not found"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null && echo "✅ Frontend stopped" || echo "⚠️  Frontend process not found"
    fi
    
    rm .server_pids
    echo ""
fi

# Kill any remaining processes on ports 8000 and 8080
echo "Cleaning up ports..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Port 8000 cleared"
lsof -ti:8080 | xargs kill -9 2>/dev/null && echo "✅ Port 8080 cleared"
echo ""

echo "========================================"
echo "✅ All servers stopped"
echo "========================================"
