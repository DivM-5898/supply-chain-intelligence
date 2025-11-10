@echo off
echo Starting AI Supplier Selection Application...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\codes\AI_IN_OPERATIONS\backend && uvicorn main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d C:\codes\AI_IN_OPERATIONS\frontend && python server.py"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   APPLICATION IS RUNNING!
echo ========================================
echo.
echo Frontend (Landing Page): http://localhost:8080
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit this window (servers will keep running)...
pause >nul

