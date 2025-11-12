# Frontend-Backend Connection Guide

## 🔌 Connection Status

**Backend API**: FastAPI on `http://localhost:8000`  
**Frontend UI**: HTTP Server on `http://localhost:8080`  
**API Base URL**: `http://localhost:8000/api/v1`

## ✅ Current Integration Status

### Already Configured

1. **CORS Configuration** ✅
   - Backend CORS origins include `http://localhost:8080` and `http://127.0.0.1:8080`
   - Configuration in: `backend/config/settings.py`

2. **API Client** ✅
   - Full-featured API client implemented in `frontend/assets/js/api.js`
   - Supports all backend endpoints
   - Proper error handling and logging

3. **API Endpoints** ✅
   - 40+ operational endpoints across 7 modules
   - All endpoints tested via integration tests
   - Swagger documentation at `/docs`

## 🚀 Starting the Application

### Option 1: Separate Terminals (Recommended for Development)

**Terminal 1 - Start Backend:**
```bash
cd /home/divyansh_maiwar/supply-chain-intelligence/backend
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Start Frontend:**
```bash
cd /home/divyansh_maiwar/supply-chain-intelligence/frontend
python server.py
```

### Option 2: Background Processes
```bash
cd /home/divyansh_maiwar/supply-chain-intelligence

# Start backend in background
source venv/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend in background
cd frontend
python server.py &
FRONTEND_PID=$!
cd ..

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8080"
echo ""
echo "To stop servers:"
echo "kill $BACKEND_PID $FRONTEND_PID"
```

## 🧪 Testing the Connection

### 1. Health Check
```bash
# Test backend health endpoint
curl http://localhost:8000/api/v1/integrated/health

# Expected response:
{
  "status": "healthy",
  "service": "Supply Chain Intelligence Platform",
  "version": "1.0.0"
}
```

### 2. API Documentation
Open in browser: `http://localhost:8000/docs`

### 3. Frontend Access
Open in browser: `http://localhost:8080`

### 4. Test API from Browser Console
Open browser console (F12) on `http://localhost:8080` and run:

```javascript
// Test API client is available
console.log('API Client:', window.api);

// Test health endpoint
window.api.request('/integrated/health')
    .then(data => console.log('Health Check:', data))
    .catch(err => console.error('Health Check Error:', err));
```

## 📋 Available API Modules

### 1. Integrated Decision Support (`/integrated`)
- `POST /evaluate-supplier` - Comprehensive 7-category evaluation
- `POST /mcda-ranking` - MCDA supplier ranking (TOPSIS/AHP/ELECTRE)
- `POST /compare-suppliers` - Side-by-side comparison
- `POST /rank-suppliers` - Multiple ranking methods
- `POST /gap-analysis` - Benchmark gap analysis
- `POST /integrated-decision-support` - Complete decision package
- `GET /health` - Service health check

### 2. Supplier Evaluation (`/suppliers`)
- `POST /evaluate` - Evaluate suppliers with ML models
- `GET /available-models` - List available ML models
- `GET /compare-models` - Compare model performance
- `POST /upload-and-evaluate` - Upload CSV and evaluate

### 3. Risk Profiling (`/risk`)
- `POST /predict` - Predict supplier risks
- `POST /anomalies` - Detect anomalies
- `GET /data-sources` - List risk data sources

### 4. Fraud Detection (`/fraud`)
- `POST /predict` - Predict fraud likelihood
- `POST /compare-models` - Compare fraud detection models
- `POST /detect/transaction` - Analyze transaction
- `POST /detect/invoice` - Analyze invoice

### 5. NLP Contract Analysis (`/contracts`)
- `POST /analyze` - Analyze contract text
- `POST /upload` - Upload contract file
- `GET /contracts` - List analyzed contracts

### 6. Decision Support (`/decision`)
- `POST /topsis` - TOPSIS ranking
- `POST /ahp` - AHP ranking

### 7. Ethics & Compliance (`/ethics`)
- `POST /explain` - Explain model predictions (LIME/SHAP)
- `POST /shap-values` - Get SHAP values
- `POST /bias-detection` - Detect model bias
- `GET /esg-scores` - Get ESG scores
- `POST /assess-compliance` - Assess compliance

### 8. Transparency (`/transparency`)
- `GET /geographic-risk` - Geographic risk analysis
- `GET /supplier-network` - Supplier network graph
- `GET /resilience-metrics` - Supply chain resilience
- `GET /transparency-scores` - Transparency scoring

### 9. Gemini AI (`/gemini`)
- `POST /analyze-contract` - AI contract analysis
- `POST /supplier-recommendations` - Get recommendations
- `POST /analyze-risk` - AI risk analysis
- `POST /generate-report` - Generate comprehensive report
- `POST /query` - Ask questions
- `GET /health` - Gemini service health

## 🔧 Frontend API Integration

### API Client Usage in Frontend

The frontend already has a fully configured API client. Here's how it works:

**1. API Configuration (`frontend/assets/js/api.js`):**
```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api/v1',
    TIMEOUT: 30000
};

// Global API client available as window.api
window.api = new APIClient();
```

**2. Making API Calls:**
```javascript
// Example: Evaluate supplier
const evaluationData = {
    supplier_id: "SUP001",
    quality_metrics: { /* ... */ },
    delivery_metrics: { /* ... */ },
    // ... other metrics
};

window.api.request('/integrated/evaluate-supplier', {
    method: 'POST',
    body: JSON.stringify(evaluationData)
})
.then(result => {
    console.log('Evaluation:', result);
    // Update UI with results
})
.catch(error => {
    console.error('Evaluation failed:', error);
    // Show error message
});
```

**3. Using Convenience Methods:**
```javascript
// Get available models
api.getAvailableModels()
    .then(models => console.log('Models:', models));

// Predict fraud
api.predictFraud(['SUP001', 'SUP002'], 'random_forest')
    .then(predictions => console.log('Fraud predictions:', predictions));

// TOPSIS ranking
api.topsisRanking({ quality: 0.4, cost: 0.3, delivery: 0.3 })
    .then(ranking => console.log('Rankings:', ranking));
```

## 🎯 Example: Complete Workflow

### Scenario: Evaluate and Rank Suppliers

```javascript
async function evaluateAndRankSuppliers() {
    try {
        // 1. Evaluate individual suppliers
        const supplier1 = await api.request('/integrated/evaluate-supplier', {
            method: 'POST',
            body: JSON.stringify({
                supplier_id: 'SUP001',
                quality_metrics: { /* ... */ },
                // ... other metrics
            })
        });
        
        const supplier2 = await api.request('/integrated/evaluate-supplier', {
            method: 'POST',
            body: JSON.stringify({
                supplier_id: 'SUP002',
                quality_metrics: { /* ... */ },
                // ... other metrics
            })
        });
        
        // 2. Compare suppliers
        const comparison = await api.request('/integrated/compare-suppliers', {
            method: 'POST',
            body: JSON.stringify({
                supplier_1_id: 'SUP001',
                supplier_2_id: 'SUP002',
                comparison_method: 'absolute'
            })
        });
        
        // 3. Perform MCDA ranking
        const ranking = await api.topsisRanking({
            quality: 0.35,
            cost: 0.25,
            delivery: 0.20,
            sustainability: 0.20
        }, ['quality', 'delivery', 'sustainability'], ['SUP001', 'SUP002']);
        
        // 4. Display results
        console.log('Evaluation Results:', { supplier1, supplier2 });
        console.log('Comparison:', comparison);
        console.log('MCDA Ranking:', ranking);
        
        return { supplier1, supplier2, comparison, ranking };
        
    } catch (error) {
        console.error('Workflow failed:', error);
        throw error;
    }
}

// Execute workflow
evaluateAndRankSuppliers()
    .then(results => console.log('Complete Results:', results));
```

## 🐛 Troubleshooting

### Issue: Backend Not Responding
**Solution:**
```bash
# Check if backend is running
ps aux | grep uvicorn

# If not running, start it
cd backend
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue: CORS Errors
**Check:**
1. Backend CORS configuration in `backend/config/settings.py`
2. Frontend is accessing correct origin (`http://localhost:8080`)

**Fix:**
```python
# backend/config/settings.py
CORS_ORIGINS: list = [
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]
```

### Issue: API Client Not Available
**Debug in Browser Console:**
```javascript
// Check if API client is loaded
console.log('API Client:', window.api);
console.log('APIClient Class:', window.APIClient);

// If undefined, check script loading order in HTML
```

### Issue: Import Errors in Backend
**Solution:**
```bash
# Ensure all dependencies are installed
cd backend
source ../venv/bin/activate
pip install -r requirements.txt
```

## 📊 Connection Verification Script

Save as `test_connection.sh`:

```bash
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
    echo "   Start with: cd backend && uvicorn main:app --reload"
fi
echo ""

# Test frontend
echo "2. Testing Frontend Availability..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>&1)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend not accessible"
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
    echo "⚠️  Check CORS configuration in backend/config/settings.py"
fi
echo ""

echo "======================================"
echo "Access Points:"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Frontend: http://localhost:8080"
echo "======================================"
```

Make executable: `chmod +x test_connection.sh`

Run: `./test_connection.sh`

## 🎉 Next Steps

1. **Start both servers** using one of the methods above
2. **Open browser** to `http://localhost:8080`
3. **Open browser console** (F12) to see API client logs
4. **Navigate through dashboard** - all API calls will be logged
5. **Test individual features** in each dashboard section

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Integration Tests**: Run `python test_integration.py` for backend validation
- **Backend Code**: `backend/` directory
- **Frontend Code**: `frontend/` directory
- **Integration Service**: `backend/services/integration_service.py`
- **API Routes**: `backend/api/routes/`

---

**Status**: ✅ Frontend and Backend are fully integrated and ready to use!

All API endpoints are accessible from the frontend via the global `window.api` client.
