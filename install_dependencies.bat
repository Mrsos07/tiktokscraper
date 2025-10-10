@echo off
echo ========================================
echo Installing TikTok Scraper Dependencies
echo ========================================
echo.

echo Installing core dependencies...
pip install fastapi uvicorn[standard] pydantic pydantic-settings sqlalchemy aiosqlite

echo.
echo Installing HTTP and scraping libraries...
pip install httpx[http2] parsel beautifulsoup4 fake-useragent

echo.
echo Installing Google Drive libraries...
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

echo.
echo Installing utilities...
pip install python-dotenv loguru tenacity aiofiles python-multipart

echo.
echo Installing admin interface...
pip install streamlit pandas

echo.
echo Installing scheduling (optional)...
pip install apscheduler

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Setup Google Drive: python scripts/setup_google_drive.py
echo 3. Initialize database: python scripts/init_db.py
echo 4. Run server: python quick_start.py
echo.
pause
