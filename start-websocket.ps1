# PowerShell script to start WebSocket Sync Service
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting WebSocket Sync Service" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend/src directory
Set-Location -Path "backend\src"

Write-Host "Starting WebSocket service on port 8004..." -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Yellow
Write-Host "  WebSocket: ws://localhost:8004/ws" -ForegroundColor White
Write-Host "  Health:    http://localhost:8004/" -ForegroundColor White
Write-Host "  Stats:     http://localhost:8004/stats" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host ""

# Start the service
python -m uvicorn services.websocket_sync.main:app --host 0.0.0.0 --port 8004 --reload
