# Fix Git and Push to GitHub
# This script removes sensitive files and pushes clean code

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fixing Git and Pushing to GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Removing sensitive files from Git..." -ForegroundColor Yellow

# Remove token.pickle if it exists in git
git rm --cached token.pickle 2>$null
git rm --cached credentials/*.json 2>$null
git rm --cached credentials/*.pickle 2>$null
git rm --cached credentials_base64.txt 2>$null
git rm --cached *.db 2>$null
git rm -r --cached logs/ 2>$null
git rm -r --cached downloads/ 2>$null

Write-Host "✓ Sensitive files removed from Git index" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Adding updated .gitignore..." -ForegroundColor Yellow
git add .gitignore

Write-Host ""
Write-Host "Step 3: Committing changes..." -ForegroundColor Yellow
git commit -m "Fix: Remove sensitive files and update .gitignore"

Write-Host ""
Write-Host "Step 4: Adding all safe files..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "Step 5: Creating commit..." -ForegroundColor Yellow
git commit -m "Initial commit: TikTok Scraper - Clean version without sensitive data"

Write-Host ""
Write-Host "Step 6: Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Successfully Pushed to GitHub! ✓" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository: https://github.com/Mrsos07/tiktokscraper" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next: Deploy on Render.com" -ForegroundColor Yellow
    Write-Host "1. Go to: https://render.com" -ForegroundColor White
    Write-Host "2. New > Blueprint" -ForegroundColor White
    Write-Host "3. Connect: Mrsos07/tiktokscraper" -ForegroundColor White
    Write-Host "4. Add environment variables" -ForegroundColor White
    Write-Host "5. Deploy!" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ Push failed!" -ForegroundColor Red
    Write-Host "Error code: $LASTEXITCODE" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Try manually:" -ForegroundColor Yellow
    Write-Host "git push -u origin main --force" -ForegroundColor White
}

Write-Host ""
