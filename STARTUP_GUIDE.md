# 🚀 Application Startup Guide

## Servers Started

### Backend Server
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Status**: ✅ Running in separate PowerShell window

### Frontend Server  
- **URL**: http://localhost:8080
- **Status**: ✅ Running in separate PowerShell window

## Access Your Application

**Main Application**: http://localhost:8080

## Features Available

1. ✅ Landing Page (Full-width, no sidebar)
2. ✅ Supplier Evaluation (7 ML Models)
3. ✅ Risk Profiling
4. ✅ Fraud Prediction
5. ✅ NLP Contract Analyzer
6. ✅ Decision Support (TOPSIS/AHP)
7. ✅ Ethics & Compliance
8. ✅ Transparency & Resilience

## Troubleshooting

### If Backend Not Running:
```powershell
cd C:\codes\AI_IN_OPERATIONS\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### If Frontend Not Running:
```powershell
cd C:\codes\AI_IN_OPERATIONS\frontend
python server.py
```

### Check Server Status:
```powershell
netstat -ano | findstr ":8000 :8080"
```

## Next Steps

1. Open browser: http://localhost:8080
2. Hard refresh: Ctrl+F5
3. Open console: F12
4. Check for `[API]` logs
5. Test dashboard tabs

