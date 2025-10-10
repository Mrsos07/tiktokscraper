# 🎵 TikTok Video Scraper & Downloader

A comprehensive, production-ready Python system for scraping and downloading TikTok videos from profiles or hashtags without login, with automatic Google Drive organization.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> ⚠️ **Disclaimer**: This tool is for educational purposes only. Users must comply with TikTok's Terms of Service and applicable laws. Use responsibly and ethically.

## Features

- 🎯 **Dual Mode**: Scrape by profile username or hashtag
- 🚀 **No Login Required**: Public content scraping with anti-blocking measures
- 💧 **No Watermark**: Multiple strategies to obtain clean video URLs
- ☁️ **Google Drive Integration**: Automatic upload with organized folder structure
- 📊 **REST API**: FastAPI with Swagger UI documentation
- 🎨 **Admin Interface**: Streamlit dashboard for job management
- ⚡ **Async & Scalable**: Concurrent downloads with job queue
- 📅 **Scheduled Jobs**: Automatic periodic scraping
- 🛡️ **Anti-Blocking**: HTTP/2, browser fingerprinting, rate limiting, proxy support

## Architecture

```
tiktok-scraper/
├── app/
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Configuration & security
│   ├── models/           # Database models
│   ├── scrapers/         # TikTok scraping logic
│   ├── downloaders/      # Video download handlers
│   ├── storage/          # Google Drive integration
│   ├── scheduler/        # Job scheduling
│   └── workers/          # Background task workers
├── admin/                # Streamlit admin interface
├── tests/                # Test suite
├── credentials/          # Google OAuth credentials
└── downloads/            # Local temporary storage
```

## 📺 Demo

```bash
# Quick start - scrape 10 videos from a profile
python scripts/test_scraper.py --mode profile --value khaby.lame --limit 10
```

## 🚀 Quick Start

**For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md)**

### 1. Installation

```bash
# Clone and navigate
cd tiktok-scraper

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configuration

```bash
# Copy environment template
copy .env.example .env

# Edit .env with your settings
```

### 3. Google Drive Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON to `credentials/google_drive_credentials.json`
6. Run initial auth: `python scripts/setup_google_drive.py`

### 4. Database Setup

```bash
# Initialize database
python scripts/init_db.py
```

### 5. Run Services

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Streamlit admin (separate terminal)
streamlit run admin/dashboard.py --server.port 8501

# Start Celery worker (optional, for distributed tasks)
celery -A app.workers.celery_worker worker --loglevel=info
```

## API Usage

### Create Scraping Job

```bash
POST http://localhost:8000/api/v1/jobs
Content-Type: application/json

{
  "mode": "profile",
  "value": "khaby.lame",
  "limit": 50,
  "no_watermark": true,
  "drive_folder_id": "optional-folder-id"
}
```

### Check Job Status

```bash
GET http://localhost:8000/api/v1/jobs/{job_id}
```

### Query Videos

```bash
GET http://localhost:8000/api/v1/videos?mode=profile&value=khaby.lame&limit=20
```

### Retry Failed Download

```bash
POST http://localhost:8000/api/v1/retries/{video_id}
```

## Google Drive Structure

Videos are organized automatically:

```
/TikTok/
├── profile/
│   └── khaby.lame/
│       └── 2025/
│           └── 01/
│               ├── 7123456789012345678.mp4
│               └── 7123456789012345678_metadata.json
└── hashtag/
    └── coldplay/
        └── 2025/
            └── 01/
                ├── 7987654321098765432.mp4
                └── 7987654321098765432_metadata.json
```

## Metadata Format

Each video includes a JSON file with:

```json
{
  "video_id": "7123456789012345678",
  "desc": "Video description",
  "author": {
    "username": "khaby.lame",
    "nickname": "Khabane Lame"
  },
  "stats": {
    "views": 1000000,
    "likes": 50000,
    "comments": 1000,
    "shares": 5000
  },
  "createdAt": "2025-01-15T10:30:00Z",
  "url": "https://www.tiktok.com/@khaby.lame/video/7123456789012345678",
  "hashtags": ["funny", "comedy"],
  "music": {
    "title": "Original Sound",
    "author": "khaby.lame"
  }
}
```

## Anti-Blocking Strategies

1. **HTTP/2**: Modern protocol support
2. **Browser Headers**: Realistic user-agent and headers
3. **Rate Limiting**: Configurable delays between requests
4. **Playwright Fallback**: Headless browser when direct requests fail
5. **Proxy Support**: Optional proxy rotation
6. **Random Delays**: Human-like behavior simulation
7. **Request Fingerprinting**: Mimics real browser requests

## Compliance & Ethics

⚠️ **Important Notes**:

- Only scrapes **public content** accessible without login
- Respects `robots.txt` and TikTok's Terms of Service
- Implements rate limiting to avoid server overload
- No collection of personal identifiable information (PII)
- Use responsibly and in accordance with local laws
- Content rights remain with original creators

## Troubleshooting

### Scraping Fails

- Check if TikTok changed their HTML structure
- Enable Playwright fallback in `.env`
- Reduce rate limits
- Use proxy if IP is blocked

### No Watermark Not Working

- TikTok frequently changes video delivery methods
- Configure external API provider in `.env`
- Some videos may not support watermark removal

### Google Drive Upload Fails

- Verify OAuth credentials are valid
- Check folder permissions
- Ensure sufficient storage space

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Code Structure

- `app/scrapers/profile_scraper.py`: Profile scraping logic
- `app/scrapers/hashtag_scraper.py`: Hashtag scraping logic
- `app/downloaders/video_downloader.py`: Video download with no-watermark
- `app/storage/google_drive.py`: Google Drive integration
- `app/api/routes/jobs.py`: Job management endpoints

## 📁 Project Structure

```
tiktok-scraper/
├── app/
│   ├── api/routes/          # FastAPI endpoints
│   ├── core/                # Configuration & logging
│   ├── models/              # Database models & schemas
│   ├── scrapers/            # TikTok scraping logic
│   ├── downloaders/         # Video download handlers
│   ├── storage/             # Google Drive integration
│   ├── scheduler/           # Job scheduling
│   └── workers/             # Background processors
├── admin/                   # Streamlit dashboard
├── scripts/                 # Utility scripts
├── tests/                   # Test suite
├── examples/                # Usage examples
├── credentials/             # Google OAuth (gitignored)
├── downloads/               # Temporary storage (gitignored)
└── logs/                    # Application logs (gitignored)
```

## 🔧 Configuration

Key settings in `.env`:

```env
# TikTok Scraping
TIKTOK_MAX_VIDEOS_PER_REQUEST=50
TIKTOK_REQUEST_DELAY_MIN=2
TIKTOK_REQUEST_DELAY_MAX=5
TIKTOK_USE_PLAYWRIGHT_FALLBACK=true

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=10

# Storage
LOCAL_STORAGE_PATH=./downloads
MAX_CONCURRENT_DOWNLOADS=5

# Google Drive
GOOGLE_DRIVE_CREDENTIALS_FILE=./credentials/google_drive_credentials.json
```

## 📊 Performance

- **Scraping Speed**: 10-50 videos/minute (depends on rate limits)
- **Download Speed**: 5-10 concurrent downloads
- **Storage**: Automatic Google Drive upload with organized folders
- **Scalability**: Horizontal scaling with multiple workers

## 🛣️ Roadmap

- [ ] WebSocket support for real-time updates
- [ ] AWS S3 and Azure Blob Storage support
- [ ] Video quality selection
- [ ] Advanced analytics dashboard
- [ ] React frontend
- [ ] Mobile app
- [ ] CLI tool
- [ ] Browser extension

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - Use responsibly and ethically. See [LICENSE](LICENSE) for details.

## ⚖️ Legal & Ethical Considerations

**Important**: This tool is for educational and research purposes only.

- ✅ Only scrapes **public content** accessible without login
- ✅ Respects `robots.txt` and rate limits
- ✅ Implements anti-blocking measures ethically
- ❌ No collection of personal identifiable information (PII)
- ❌ No circumvention of authentication
- ❌ No violation of TikTok's Terms of Service

**Users are responsible for**:
- Complying with TikTok's Terms of Service
- Respecting copyright and intellectual property rights
- Following local laws and regulations (GDPR, CCPA, etc.)
- Using scraped content appropriately
- Giving proper attribution to content creators

## 📞 Support

- 📖 [Documentation](README.md)
- 🚀 [Quick Start Guide](QUICKSTART.md)
- 🔌 [API Documentation](API_DOCUMENTATION.md)
- 🚢 [Deployment Guide](DEPLOYMENT.md)
- 💡 [Examples](examples/)
- 🐛 [Issue Tracker](https://github.com/yourusername/tiktok-scraper/issues)

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Playwright](https://playwright.dev/) - Browser automation
- [Streamlit](https://streamlit.io/) - Admin interface
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Google Drive API](https://developers.google.com/drive) - Cloud storage

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Made with ❤️ for the developer community**

**Remember**: Use this tool responsibly and ethically. Respect content creators and platform policies.
