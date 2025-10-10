# Script to install Playwright and Chromium
# Run this script to fix the "No videos found" error

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Playwright Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv is activated
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment is activated" -ForegroundColor Green
} else {
    Write-Host "⚠️  Virtual environment not activated" -ForegroundColor Yellow
    Write-Host "   Activating venv..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

Write-Host ""
Write-Host "Step 1: Installing Playwright library..." -ForegroundColor Cyan
pip install --upgrade playwright

Write-Host ""
Write-Host "Step 2: Installing Chromium browser..." -ForegroundColor Cyan
playwright install chromium

Write-Host ""
Write-Host "Step 3: Verifying installation..." -ForegroundColor Cyan

# Test Playwright
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright library OK')"

# Test Chromium
$chromiumTest = playwright --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Chromium installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Chromium installation failed" -ForegroundColor Red
    Write-Host "   Try running: python -m playwright install chromium" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart the server: python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "2. Try creating a job again" -ForegroundColor White
Write-Host ""
