# Final Push - Clean Repository
Write-Host "Fixing and pushing to GitHub..." -ForegroundColor Cyan

# Remove .git folder completely
Remove-Item -Path .git -Recurse -Force -ErrorAction SilentlyContinue

# Remove sensitive files
Remove-Item -Path token.pickle -Force -ErrorAction SilentlyContinue
Remove-Item -Path credentials_base64.txt -Force -ErrorAction SilentlyContinue
Remove-Item -Path *.db -Force -ErrorAction SilentlyContinue

# Initialize fresh git
git init
git branch -M main

# Add remote
git remote add origin https://github.com/Mrsos07/tiktokscraper.git

# Add all files (gitignore will handle exclusions)
git add .

# Commit
git commit -m "Initial commit: TikTok Scraper with Auto Monitoring"

# Force push
git push -u origin main --force

Write-Host ""
Write-Host "Done! Check: https://github.com/Mrsos07/tiktokscraper" -ForegroundColor Green
