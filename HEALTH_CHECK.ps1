# Health Check Script - Check if services are running properly

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TikTok Scraper - Health Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker containers
Write-Host "Checking Docker containers..." -ForegroundColor Yellow
$containers = docker compose ps --format json | ConvertFrom-Json

if ($containers.Count -eq 0) {
    Write-Host "✗ No containers running!" -ForegroundColor Red
    Write-Host "Run .\DEPLOY.ps1 to start services" -ForegroundColor Yellow
    exit 1
}

foreach ($container in $containers) {
    $name = $container.Service
    $state = $container.State
    
    if ($state -eq "running") {
        Write-Host "✓ $name is running" -ForegroundColor Green
    } else {
        Write-Host "✗ $name is $state" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Checking API endpoint..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API is responding (Status: 200)" -ForegroundColor Green
    } else {
        Write-Host "⚠ API responded with status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ API is not responding" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Checking Dashboard..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Dashboard is responding (Status: 200)" -ForegroundColor Green
    } else {
        Write-Host "⚠ Dashboard responded with status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Dashboard is not responding" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Health Check Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor White
Write-Host "  • API:       http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  • Dashboard: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
