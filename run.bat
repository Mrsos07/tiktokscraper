@echo off
REM TikTok Scraper - Windows Run Script

echo ========================================
echo TikTok Scraper - Starting Services
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
    playwright install chromium
) else (
    call venv\Scripts\activate.bat
)

REM Check if .env exists
if not exist ".env" (
    echo .env file not found. Copying from .env.example...
    copy .env.example .env
    echo Please edit .env file with your settings and run again.
    pause
    exit /b
)

REM Check if database exists
if not exist "tiktok_scraper.db" (
    echo Database not found. Initializing...
    python scripts\init_db.py
)

echo.
echo Select service to run:
echo 1. API Server (FastAPI)
echo 2. Admin Dashboard (Streamlit)
echo 3. Both (API + Admin)
echo 4. Test Scraper
echo 5. Setup Google Drive
echo 6. Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto api
if "%choice%"=="2" goto admin
if "%choice%"=="3" goto both
if "%choice%"=="4" goto test
if "%choice%"=="5" goto setup
if "%choice%"=="6" goto end

:api
echo.
echo Starting API Server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
goto end

:admin
echo.
echo Starting Admin Dashboard on http://localhost:8501
echo.
streamlit run admin\dashboard.py --server.port 8501
goto end

:both
echo.
echo Starting both services...
echo API: http://localhost:8000
echo Admin: http://localhost:8501
echo.
start "TikTok Scraper API" cmd /k "call venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
start "TikTok Scraper Admin" cmd /k "call venv\Scripts\activate.bat && streamlit run admin\dashboard.py --server.port 8501"
echo.
echo Services started in separate windows.
echo Press any key to exit this window...
pause >nul
goto end

:test
echo.
set /p mode="Enter mode (profile/hashtag): "
set /p value="Enter username or hashtag: "
set /p limit="Enter limit (default 5): "
if "%limit%"=="" set limit=5
echo.
python scripts\test_scraper.py --mode %mode% --value %value% --limit %limit%
echo.
pause
goto end

:setup
echo.
echo Setting up Google Drive authentication...
echo.
python scripts\setup_google_drive.py
echo.
pause
goto end

:end
echo.
echo Goodbye!
deactivate
