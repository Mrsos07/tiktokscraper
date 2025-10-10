# Check Python Versions Script
# This will show all available Python versions on your system

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Python Version Checker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check default Python
Write-Host "Checking default Python..." -ForegroundColor Cyan
try {
    $defaultPython = python --version 2>&1
    Write-Host "Default Python: $defaultPython" -ForegroundColor Yellow
    
    if ($defaultPython -match "3.13") {
        Write-Host "⚠️  WARNING: Python 3.13 is NOT compatible with Playwright!" -ForegroundColor Red
    } elseif ($defaultPython -match "3.12") {
        Write-Host "✅ Python 3.12 - Perfect!" -ForegroundColor Green
    } elseif ($defaultPython -match "3.11") {
        Write-Host "✅ Python 3.11 - Good!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Python not found in PATH" -ForegroundColor Red
}

Write-Host ""
Write-Host "Checking for specific versions..." -ForegroundColor Cyan
Write-Host ""

# Check Python 3.12
Write-Host "Python 3.12:" -NoNewline
try {
    $py312 = py -3.12 --version 2>&1
    if ($py312 -match "3.12") {
        Write-Host " ✅ $py312" -ForegroundColor Green
        Write-Host "  Command: py -3.12" -ForegroundColor Gray
    } else {
        Write-Host " ❌ Not found" -ForegroundColor Red
    }
} catch {
    Write-Host " ❌ Not found" -ForegroundColor Red
}

Write-Host ""

# Check Python 3.11
Write-Host "Python 3.11:" -NoNewline
try {
    $py311 = py -3.11 --version 2>&1
    if ($py311 -match "3.11") {
        Write-Host " ✅ $py311" -ForegroundColor Green
        Write-Host "  Command: py -3.11" -ForegroundColor Gray
    } else {
        Write-Host " ❌ Not found" -ForegroundColor Red
    }
} catch {
    Write-Host " ❌ Not found" -ForegroundColor Red
}

Write-Host ""

# Check Python 3.13
Write-Host "Python 3.13:" -NoNewline
try {
    $py313 = py -3.13 --version 2>&1
    if ($py313 -match "3.13") {
        Write-Host " ⚠️  $py313" -ForegroundColor Yellow
        Write-Host "  ⚠️  NOT compatible with Playwright!" -ForegroundColor Red
    } else {
        Write-Host " ❌ Not found" -ForegroundColor Gray
    }
} catch {
    Write-Host " ❌ Not found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Recommendation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Determine recommendation
$hasPython312 = $false
$hasPython311 = $false

try {
    $test312 = py -3.12 --version 2>&1
    if ($test312 -match "3.12") { $hasPython312 = $true }
} catch {}

try {
    $test311 = py -3.11 --version 2>&1
    if ($test311 -match "3.11") { $hasPython311 = $true }
} catch {}

if ($hasPython312) {
    Write-Host "✅ You have Python 3.12 - Perfect!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Run this command to create the environment:" -ForegroundColor Yellow
    Write-Host ".\setup_fresh_env.ps1" -ForegroundColor Cyan
} elseif ($hasPython311) {
    Write-Host "✅ You have Python 3.11 - Good!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Run this command to create the environment:" -ForegroundColor Yellow
    Write-Host ".\setup_fresh_env.ps1" -ForegroundColor Cyan
} else {
    Write-Host "❌ You need to install Python 3.12!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Download from:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/release/python-3120/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Choose: Windows installer (64-bit)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "During installation:" -ForegroundColor Yellow
    Write-Host "  ✅ Check 'Add Python to PATH'" -ForegroundColor White
    Write-Host "  ✅ Check 'Install for all users'" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
