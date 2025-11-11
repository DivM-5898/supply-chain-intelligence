# Test Backend APIs
Write-Host "`n========================================"
Write-Host "Testing Backend API Endpoints"
Write-Host "========================================`n"

# Test 1: Health Check
Write-Host "1. Testing Health Endpoint..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "   ✅ Health Check: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Root Endpoint
Write-Host "`n2. Testing Root Endpoint..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
    Write-Host "   ✅ Root Endpoint: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Root Endpoint Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Available Models
Write-Host "`n3. Testing Available Models..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/suppliers/available-models" -Method Get
    Write-Host "   ✅ Available Models: $($response.available_models.Count) models found" -ForegroundColor Green
    Write-Host "   Models: $($response.available_models -join ', ')" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Available Models Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Error Details: $($_.Exception.Response)" -ForegroundColor Yellow
}

# Test 4: Supplier Evaluation
Write-Host "`n4. Testing Supplier Evaluation..."
try {
    $body = @{
        supplier_ids = $null
        model_type = "xgboost"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/suppliers/evaluate" -Method Post -Body $body -ContentType "application/json"
    Write-Host "   ✅ Supplier Evaluation: $($response.total_suppliers) suppliers evaluated" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Supplier Evaluation Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Error Response: $responseBody" -ForegroundColor Yellow
    }
}

# Test 5: Risk Prediction
Write-Host "`n5. Testing Risk Prediction..."
try {
    $body = @{
        supplier_ids = $null
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/risk/predict" -Method Post -Body $body -ContentType "application/json"
    Write-Host "   ✅ Risk Prediction: $($response.total_suppliers) suppliers analyzed" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Risk Prediction Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Error Response: $responseBody" -ForegroundColor Yellow
    }
}

# Test 6: Fraud Prediction
Write-Host "`n6. Testing Fraud Prediction..."
try {
    $body = @{
        supplier_ids = $null
        model_type = "random_forest"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/fraud/predict" -Method Post -Body $body -ContentType "application/json"
    Write-Host "   ✅ Fraud Prediction: $($response.total_suppliers) suppliers analyzed" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Fraud Prediction Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Error Response: $responseBody" -ForegroundColor Yellow
    }
}

# Test 7: Compare Models
Write-Host "`n7. Testing Compare Models..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/suppliers/compare-models?models=xgboost,random_forest" -Method Get
    Write-Host "   ✅ Compare Models: $($response.total_suppliers) suppliers compared" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Compare Models Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n========================================"
Write-Host "API Testing Complete"
Write-Host "========================================`n"

