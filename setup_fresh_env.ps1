# Fresh Environment Setup Script
# This will create a new virtual environment with Python 3.12 and install everything correctly

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fresh Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python version
Write-Host "Checking Python versions..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
Write-Host "Current Python: $pythonVersion" -ForegroundColor Yellow

# Try to find Python 3.12
$python312 = $null
try {
    $python312 = py -3.12 --version 2>&1
    if ($python312 -match "3.12") {
        Write-Host "✅ Found Python 3.12" -ForegroundColor Green
        $pythonCmd = "py -3.12"
    }
} catch {
    Write-Host "⚠️  Python 3.12 not found" -ForegroundColor Yellow
}

# Try Python 3.11 as fallback
if (-not $python312) {
    try {
        $python311 = py -3.11 --version 2>&1
        if ($python311 -match "3.11") {
            Write-Host "✅ Found Python 3.11 (using as fallback)" -ForegroundColor Green
            $pythonCmd = "py -3.11"
        }
    } catch {
        Write-Host "⚠️  Python 3.11 not found" -ForegroundColor Yellow
    }
}

# Check if we found a compatible version
if (-not $pythonCmd) {
    Write-Host "" -ForegroundColor Red
    Write-Host "❌ ERROR: Python 3.12 or 3.11 not found!" -ForegroundColor Red
    Write-Host "" -ForegroundColor Red
    Write-Host "Python 3.13 is NOT compatible with Playwright on Windows!" -ForegroundColor Red
    Write-Host "" -ForegroundColor Yellow
    Write-Host "Please install Python 3.12:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/release/python-3120/" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor Yellow
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "" -ForegroundColor Green
Write-Host "Using: $pythonCmd" -ForegroundColor Green
Write-Host "" -ForegroundColor Cyan

# Step 2: Remove old venv if exists
if (Test-Path "env") {
    Write-Host "Removing old 'env' directory..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "env"
}

# Step 3: Create new virtual environment with correct Python version
Write-Host "Creating new virtual environment 'env' with $pythonCmd..." -ForegroundColor Cyan
Invoke-Expression "$pythonCmd -m venv env"

# Step 3: Activate the new environment
Write-Host "Activating new environment..." -ForegroundColor Cyan
& ".\env\Scripts\Activate.ps1"

# Step 4: Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Step 5: Install core dependencies with HTTP/2 support
Write-Host ""
Write-Host "Installing core dependencies..." -ForegroundColor Cyan
pip install "httpx[http2]"
pip install fastapi uvicorn[standard]
pip install pydantic pydantic-settings

# Step 6: Install scraping dependencies
Write-Host ""
Write-Host "Installing scraping dependencies..." -ForegroundColor Cyan
pip install playwright parsel beautifulsoup4 fake-useragent tenacity

# Step 7: Install Playwright browsers
Write-Host ""
Write-Host "Installing Playwright Chromium..." -ForegroundColor Cyan
playwright install chromium

# Step 8: Install database dependencies
Write-Host ""
Write-Host "Installing database dependencies..." -ForegroundColor Cyan
pip install sqlalchemy alembic aiosqlite

# Step 9: Install Google Drive dependencies
Write-Host ""
Write-Host "Installing Google Drive dependencies..." -ForegroundColor Cyan
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Step 10: Install other dependencies
Write-Host ""
Write-Host "Installing other dependencies..." -ForegroundColor Cyan
pip install streamlit pandas
pip install apscheduler celery[redis] redis
pip install python-dotenv python-multipart aiofiles
pip install loguru prometheus-client
pip install pytest pytest-asyncio httpx-mock

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Activate environment: .\env\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Start API server: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host "3. Start dashboard: streamlit run admin/dashboard.py" -ForegroundColor White
Write-Host ""
Write-Host "Test the scraper:" -ForegroundColor Yellow
Write-Host 'curl -X POST "http://localhost:8000/api/v1/jobs" -H "Content-Type: application/json" -d "{\"mode\": \"profile\", \"value\": \"mikaylanogueira\", \"limit\": 2}"' -ForegroundColor White
Write-Host ""
