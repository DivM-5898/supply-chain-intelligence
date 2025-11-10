# Quick Server Status Check
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 SERVER STATUS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Backend
$backend = netstat -ano | findstr ":8000" | Select-String "LISTENING"
if ($backend) {
    Write-Host "✅ Backend: http://localhost:8000 (RUNNING)" -ForegroundColor Green
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        Write-Host "   Health Check: OK" -ForegroundColor Green
    } catch {
        Write-Host "   Health Check: Failed" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Backend: NOT RUNNING" -ForegroundColor Red
}

# Check Frontend
$frontend = netstat -ano | findstr ":8080" | Select-String "LISTENING"
if ($frontend) {
    Write-Host "✅ Frontend: http://localhost:8080 (RUNNING)" -ForegroundColor Green
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -UseBasicParsing -TimeoutSec 2
        Write-Host "   Page Load: OK" -ForegroundColor Green
    } catch {
        Write-Host "   Page Load: Failed" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Frontend: NOT RUNNING" -ForegroundColor Red
}

Write-Host ""
Write-Host "📍 Open http://localhost:8080 in your browser" -ForegroundColor Yellow
Write-Host ""

