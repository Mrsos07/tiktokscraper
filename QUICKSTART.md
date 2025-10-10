# Quick Start Guide

Get up and running with TikTok Scraper in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- Google account (for Drive storage)
- 2GB+ free disk space

## Installation (Windows)

### 1. Quick Setup

```bash
# Navigate to project directory
cd tiktok-scraper

# Run the setup script
run.bat
```

The script will:
- Create virtual environment
- Install all dependencies
- Install Playwright browser
- Copy .env template

### 2. Configure Environment

Edit `.env` file with your settings:

```env
# Minimum required settings
GOOGLE_DRIVE_CREDENTIALS_FILE=./credentials/google_drive_credentials.json
TIKTOK_MAX_VIDEOS_PER_REQUEST=50
```

### 3. Setup Google Drive

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials to `credentials/google_drive_credentials.json`

Run setup:
```bash
python scripts/setup_google_drive.py
```

### 4. Initialize Database

```bash
python scripts/init_db.py
```

### 5. Start Services

**Option A: Run both services**
```bash
run.bat
# Select option 3
```

**Option B: Run separately**

Terminal 1 - API:
```bash
uvicorn app.main:app --reload
```

Terminal 2 - Admin:
```bash
streamlit run admin/dashboard.py
```

## Installation (Linux/Mac)

```bash
# Make script executable
chmod +x run.sh

# Run setup
./run.sh
```

Follow steps 2-5 from Windows guide above.

## First Usage

### Via Admin Dashboard

1. Open http://localhost:8501
2. Go to "Create Job" page
3. Fill in:
   - Mode: `profile` or `hashtag`
   - Value: `khaby.lame` (example)
   - Limit: `10`
   - No Watermark: ✓
4. Click "Create Job"
5. Monitor progress in "Jobs" page

### Via API

```bash
# Create job
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "profile",
    "value": "khaby.lame",
    "limit": 10,
    "no_watermark": true
  }'

# Check status (replace JOB_ID)
curl http://localhost:8000/api/v1/jobs/JOB_ID
```

### Via Python

```python
import requests

# Create job
response = requests.post("http://localhost:8000/api/v1/jobs", json={
    "mode": "profile",
    "value": "khaby.lame",
    "limit": 10,
    "no_watermark": True
})

job = response.json()
print(f"Job created: {job['id']}")
```

## Testing

Test scraper without creating a job:

```bash
# Test profile scraping
python scripts/test_scraper.py --mode profile --value khaby.lame --limit 5

# Test hashtag scraping
python scripts/test_scraper.py --mode hashtag --value funny --limit 5
```

## Access Points

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

## Common Issues

### Issue: "Module not found"
**Solution**: Activate virtual environment
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Issue: "Google Drive credentials not found"
**Solution**: Follow step 3 to setup Google Drive

### Issue: "Playwright browser not found"
**Solution**: Install browser
```bash
playwright install chromium
```

### Issue: "Port already in use"
**Solution**: Change port in command
```bash
uvicorn app.main:app --port 8001
streamlit run admin/dashboard.py --server.port 8502
```

### Issue: "Scraping returns no videos"
**Solution**: 
- Check if username/hashtag is correct
- Enable Playwright fallback in `.env`
- Check logs in `logs/` directory

## Next Steps

1. **Read Documentation**
   - [README.md](README.md) - Full documentation
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

2. **Explore Examples**
   - Check `examples/basic_usage.py` for Python examples
   - Try different scraping modes and filters

3. **Setup Scheduled Jobs**
   - Create recurring jobs in admin dashboard
   - Automate daily/weekly scraping

4. **Customize**
   - Adjust rate limits in `.env`
   - Configure proxy if needed
   - Add external no-watermark API

## Getting Help

- Check [README.md](README.md) for detailed documentation
- Review logs in `logs/` directory
- Open an issue on GitHub
- Check API docs at http://localhost:8000/docs

## Quick Commands Reference

```bash
# Start API
uvicorn app.main:app --reload

# Start Admin
streamlit run admin/dashboard.py

# Initialize DB
python scripts/init_db.py

# Setup Google Drive
python scripts/setup_google_drive.py

# Test scraper
python scripts/test_scraper.py --mode profile --value username --limit 5

# Run tests
pytest tests/

# View logs
tail -f logs/app_*.log  # Linux/Mac
type logs\app_*.log     # Windows
```

## Success Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Google Drive credentials setup
- [ ] Database initialized
- [ ] API server running
- [ ] Admin dashboard accessible
- [ ] First job created successfully
- [ ] Videos downloaded to Google Drive

Congratulations! You're ready to use TikTok Scraper! 🎉
