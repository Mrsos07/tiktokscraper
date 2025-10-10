# Push to GitHub Script
# Repository: https://github.com/Mrsos07/tiktokscraper.git

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Pushing to GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    git --version | Out-Null
    Write-Host "✓ Git is installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 1: Initialize Git repository..." -ForegroundColor Yellow
git init

Write-Host ""
Write-Host "Step 2: Add remote repository..." -ForegroundColor Yellow
git remote add origin https://github.com/Mrsos07/tiktokscraper.git

Write-Host ""
Write-Host "Step 3: Configure Git user..." -ForegroundColor Yellow
Write-Host "Enter your GitHub username:" -ForegroundColor Cyan
$username = Read-Host
git config user.name "$username"

Write-Host "Enter your GitHub email:" -ForegroundColor Cyan
$email = Read-Host
git config user.email "$email"

Write-Host ""
Write-Host "Step 4: Add all files..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "Step 5: Create initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: TikTok Scraper with Auto Monitoring and Cloud Deployment"

Write-Host ""
Write-Host "Step 6: Push to GitHub..." -ForegroundColor Yellow
Write-Host "You may be asked for GitHub credentials..." -ForegroundColor Cyan
git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Successfully Pushed to GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository: https://github.com/Mrsos07/tiktokscraper" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps for Render.com Deployment:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://render.com" -ForegroundColor White
    Write-Host "2. Sign in with GitHub" -ForegroundColor White
    Write-Host "3. Click: New > Blueprint" -ForegroundColor White
    Write-Host "4. Select: Mrsos07/tiktokscraper" -ForegroundColor White
    Write-Host "5. Render will detect render.yaml automatically" -ForegroundColor White
    Write-Host "6. Add Environment Variables:" -ForegroundColor White
    Write-Host "   - GOOGLE_DRIVE_CREDENTIALS_BASE64 (from credentials_base64.txt)" -ForegroundColor Gray
    Write-Host "   - GOOGLE_DRIVE_FOLDER_ID" -ForegroundColor Gray
    Write-Host "7. Click: Apply" -ForegroundColor White
    Write-Host ""
    Write-Host "Your app will be live in ~5 minutes! 🚀" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✗ Push failed!" -ForegroundColor Red
    Write-Host "Please check your GitHub credentials and try again" -ForegroundColor Yellow
}

Write-Host ""
