#!/bin/bash

echo "======================================"
echo "Frontend-Backend Connection Test"
echo "======================================"
echo ""

# Test backend
echo "1. Testing Backend Health..."
BACKEND_RESPONSE=$(curl -s http://localhost:8000/api/v1/integrated/health 2>&1)
if [ $? -eq 0 ]; then
    echo "✅ Backend is responsive"
    echo "   Response: $BACKEND_RESPONSE"
else
    echo "❌ Backend not responding"
    echo "   Start with: cd backend && source ../venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
fi
echo ""

# Test frontend
echo "2. Testing Frontend Availability..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>&1)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend not accessible (HTTP $FRONTEND_RESPONSE)"
    echo "   Start with: cd frontend && python server.py"
fi
echo ""

# Test CORS
echo "3. Testing CORS Configuration..."
CORS_TEST=$(curl -s -H "Origin: http://localhost:8080" \
                -H "Access-Control-Request-Method: POST" \
                -H "Access-Control-Request-Headers: Content-Type" \
                -X OPTIONS http://localhost:8000/api/v1/integrated/health -v 2>&1)
if echo "$CORS_TEST" | grep -q "Access-Control-Allow-Origin"; then
    echo "✅ CORS configured correctly"
else
    echo "⚠️  Cannot verify CORS (backend may not be running)"
    echo "   Check backend/config/settings.py if errors occur"
fi
echo ""

# Test virtual environment
echo "4. Checking Virtual Environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
    if [ -f "venv/bin/activate" ]; then
        echo "   Activation script: venv/bin/activate"
    fi
else
    echo "⚠️  Virtual environment not found"
    echo "   Create with: python3 -m venv venv"
    echo "   Install deps: pip install -r backend/requirements.txt"
fi
echo ""

echo "======================================"
echo "Access Points:"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Frontend: http://localhost:8080"
echo "======================================"
echo ""
echo "Quick Start:"
echo "  Terminal 1: cd backend && source ../venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo "  Terminal 2: cd frontend && python server.py"
echo "======================================"
