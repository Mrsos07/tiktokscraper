# Prepare for Cloud Deployment
# This script helps you prepare the app for cloud deployment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cloud Deployment Preparation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if credentials.json exists
if (Test-Path "credentials\credentials.json") {
    Write-Host "✓ credentials.json found" -ForegroundColor Green
    
    # Convert to base64
    Write-Host ""
    Write-Host "Converting credentials to base64..." -ForegroundColor Yellow
    
    $credentials = Get-Content "credentials\credentials.json" -Raw
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($credentials)
    $base64 = [Convert]::ToBase64String($bytes)
    
    # Save to file
    $base64 | Out-File "credentials_base64.txt" -Encoding utf8
    
    Write-Host "✓ Base64 credentials saved to: credentials_base64.txt" -ForegroundColor Green
    Write-Host ""
    Write-Host "Copy this value and set as environment variable:" -ForegroundColor Yellow
    Write-Host "GOOGLE_DRIVE_CREDENTIALS_BASE64" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "First 100 characters:" -ForegroundColor White
    Write-Host $base64.Substring(0, [Math]::Min(100, $base64.Length)) -ForegroundColor Gray
    Write-Host "..." -ForegroundColor Gray
    
} else {
    Write-Host "✗ credentials.json not found in ./credentials/" -ForegroundColor Red
    Write-Host "Please add your Google Drive credentials first" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Choose Your Cloud Platform" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Railway.app (Recommended)" -ForegroundColor Green
Write-Host "   - Free tier available" -ForegroundColor White
Write-Host "   - Easy to use" -ForegroundColor White
Write-Host "   - Command: railway login && railway init && railway up" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Render.com" -ForegroundColor Green
Write-Host "   - Free tier available" -ForegroundColor White
Write-Host "   - Auto-deploy from GitHub" -ForegroundColor White
Write-Host "   - Uses: render.yaml" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Fly.io" -ForegroundColor Green
Write-Host "   - Good free tier" -ForegroundColor White
Write-Host "   - Global deployment" -ForegroundColor White
Write-Host "   - Command: fly launch && fly deploy" -ForegroundColor Gray
Write-Host ""

Write-Host "4. DigitalOcean App Platform" -ForegroundColor Green
Write-Host "   - $5/month minimum" -ForegroundColor White
Write-Host "   - Reliable and stable" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Choose a platform above" -ForegroundColor Yellow
Write-Host "2. Read: CLOUD_DEPLOYMENT.md for detailed instructions" -ForegroundColor Yellow
Write-Host "3. Set environment variables (especially GOOGLE_DRIVE_CREDENTIALS_BASE64)" -ForegroundColor Yellow
Write-Host "4. Deploy!" -ForegroundColor Yellow
Write-Host ""

Write-Host "Files created for deployment:" -ForegroundColor White
Write-Host "  ✓ Dockerfile" -ForegroundColor Green
Write-Host "  ✓ docker-compose.yml" -ForegroundColor Green
Write-Host "  ✓ railway.toml" -ForegroundColor Green
Write-Host "  ✓ render.yaml" -ForegroundColor Green
Write-Host "  ✓ fly.toml" -ForegroundColor Green
Write-Host "  ✓ Procfile" -ForegroundColor Green
Write-Host ""

Write-Host "Quick Start - Railway.app:" -ForegroundColor Cyan
Write-Host "  npm install -g @railway/cli" -ForegroundColor White
Write-Host "  railway login" -ForegroundColor White
Write-Host "  railway init" -ForegroundColor White
Write-Host "  railway up" -ForegroundColor White
Write-Host ""
