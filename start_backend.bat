@echo off
echo ========================================
echo   AI Supplier Selection - Backend
echo ========================================
echo.
echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

