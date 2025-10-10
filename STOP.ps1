# Stop Docker Containers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stopping TikTok Scraper Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

docker compose stop

Write-Host ""
Write-Host "✓ All services stopped" -ForegroundColor Green
Write-Host ""
Write-Host "To start again, run: .\DEPLOY.ps1" -ForegroundColor Yellow
Write-Host "To remove containers: docker compose down" -ForegroundColor Yellow
Write-Host ""
