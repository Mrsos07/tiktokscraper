# Start Both Servers Script
# Run this after setting up the environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting TikTok Scraper Servers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if env is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating environment..." -ForegroundColor Yellow
    & ".\env\Scripts\Activate.ps1"
}

Write-Host "Starting API Server on port 8000..." -ForegroundColor Cyan
Write-Host "API will be available at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

# Start API server in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\env\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

Write-Host "Starting Streamlit Dashboard on port 8501..." -ForegroundColor Cyan
Write-Host "Dashboard will be available at: http://localhost:8501" -ForegroundColor Green
Write-Host ""

# Start Streamlit in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\env\Scripts\Activate.ps1; streamlit run admin/dashboard.py"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Both servers are starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API Server: http://localhost:8000/docs" -ForegroundColor White
Write-Host "Dashboard: http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
