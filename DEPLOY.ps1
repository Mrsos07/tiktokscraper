# Deploy Script - Build and Start Docker Containers
# Run this to deploy the application using Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TikTok Scraper - Docker Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✓ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if docker-compose is available
try {
    docker compose version | Out-Null
    Write-Host "✓ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose is not available!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Building Docker images..." -ForegroundColor Cyan
docker compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✓ Build completed successfully" -ForegroundColor Green
Write-Host ""
Write-Host "Starting containers..." -ForegroundColor Cyan
docker compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to start containers!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deployment Successful!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services are now running:" -ForegroundColor White
Write-Host "  • API Server:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  • API Docs:    http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  • Dashboard:   http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  • View logs:       docker compose logs -f" -ForegroundColor White
Write-Host "  • Stop services:   docker compose stop" -ForegroundColor White
Write-Host "  • Restart:         docker compose restart" -ForegroundColor White
Write-Host "  • Remove all:      docker compose down" -ForegroundColor White
Write-Host ""
Write-Host "Checking container status..." -ForegroundColor Cyan
docker compose ps
Write-Host ""
