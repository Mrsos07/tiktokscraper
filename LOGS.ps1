# View Docker Container Logs

param(
    [string]$Service = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TikTok Scraper - Container Logs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Service -eq "") {
    Write-Host "Showing logs for all services..." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to exit" -ForegroundColor Yellow
    Write-Host ""
    docker compose logs -f
} else {
    Write-Host "Showing logs for: $Service" -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to exit" -ForegroundColor Yellow
    Write-Host ""
    docker compose logs -f $Service
}
