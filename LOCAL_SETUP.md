# 🚀 Local Development Setup Guide

## Quick Start (Windows)

### Option 1: Using the Startup Script (Easiest)

1. **Double-click** `start_app.bat` in the project root
   - This will automatically start both backend and frontend servers

2. **Access the application:**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## Manual Setup (Step-by-Step)

### Prerequisites
- Python 3.8+ installed
- pip (Python package manager)

### Step 1: Setup Backend

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start backend server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   Backend will run on: **http://localhost:8000**

### Step 2: Setup Frontend

1. **Open a NEW terminal window** (keep backend running)

2. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

3. **Start frontend server:**
   ```bash
   python server.py
   ```

   Frontend will run on: **http://localhost:8080**

---

## Verification

### Check Backend Health
Open browser: http://localhost:8000/health
Should return: `{"status":"healthy"}`

### Check Frontend
Open browser: http://localhost:8080
Should show the landing page

### Check API Documentation
Open browser: http://localhost:8000/docs
Should show Swagger UI with all API endpoints

---

## Troubleshooting

### Port Already in Use
If port 8000 or 8080 is already in use:

**Backend (change port):**
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Frontend (edit `frontend/server.py`):**
Change `PORT = 8080` to `PORT = 8081`

### Python Not Found
- Make sure Python is installed and added to PATH
- Check: `python --version`

### Dependencies Installation Fails
- Upgrade pip: `python -m pip install --upgrade pip`
- Install dependencies one by one if needed

### Models Not Found
- Models are pre-trained and should be in `backend/models/saved_models/`
- If missing, run: `python backend/train_models.py`

---

## Project Structure

```
AI_IN_OPERATIONS/
├── backend/          # FastAPI backend server
│   ├── main.py      # Entry point
│   ├── api/         # API routes
│   ├── services/    # Business logic
│   └── models/      # ML models
├── frontend/        # HTML/CSS/JS frontend
│   ├── index.html   # Main page
│   ├── server.py    # Frontend server
│   └── assets/      # CSS, JS files
└── start_app.bat    # Quick start script
```

---

## Environment Variables (Optional)

Create `.env` file in `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

---

## Stopping Servers

- Press `Ctrl+C` in each terminal window
- Or close the terminal windows
- Or use Task Manager to kill Python processes

---

## Need Help?

- Check backend logs in the terminal
- Check browser console (F12) for frontend errors
- Verify both servers are running: `netstat -ano | findstr ":8000 :8080"`

