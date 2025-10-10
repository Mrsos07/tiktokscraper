# Deployment Guide

## Local Development

### Prerequisites
- Python 3.10+
- Google Cloud account with Drive API enabled
- (Optional) Redis for distributed tasks

### Setup

1. **Clone and setup environment**
```bash
cd tiktok-scraper
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
playwright install chromium
```

2. **Configure environment**
```bash
copy .env.example .env
# Edit .env with your settings
```

3. **Setup Google Drive**
- Create OAuth credentials in Google Cloud Console
- Download credentials JSON to `credentials/google_drive_credentials.json`
- Run: `python scripts/setup_google_drive.py`

4. **Initialize database**
```bash
python scripts/init_db.py
```

5. **Run services**
```bash
# Terminal 1: API
uvicorn app.main:app --reload

# Terminal 2: Admin Dashboard
streamlit run admin/dashboard.py
```

## Docker Deployment

### Using Docker Compose

1. **Build and start all services**
```bash
docker-compose up -d
```

This starts:
- FastAPI API (port 8000)
- Streamlit Admin (port 8501)
- PostgreSQL database
- Redis
- Celery worker

2. **View logs**
```bash
docker-compose logs -f api
docker-compose logs -f worker
```

3. **Stop services**
```bash
docker-compose down
```

## Production Deployment

### Using Systemd (Linux)

1. **Create service file** `/etc/systemd/system/tiktok-scraper-api.service`
```ini
[Unit]
Description=TikTok Scraper API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/tiktok-scraper
Environment="PATH=/opt/tiktok-scraper/venv/bin"
ExecStart=/opt/tiktok-scraper/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

2. **Enable and start**
```bash
sudo systemctl enable tiktok-scraper-api
sudo systemctl start tiktok-scraper-api
```

### Using Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Cloud Deployment

#### AWS EC2

1. Launch EC2 instance (t3.medium or larger)
2. Install Docker and Docker Compose
3. Clone repository
4. Configure environment variables
5. Run `docker-compose up -d`
6. Configure security groups (ports 8000, 8501)

#### Google Cloud Run

1. Build container image
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/tiktok-scraper
```

2. Deploy to Cloud Run
```bash
gcloud run deploy tiktok-scraper \
  --image gcr.io/PROJECT_ID/tiktok-scraper \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Heroku

1. Create Heroku app
```bash
heroku create tiktok-scraper
```

2. Add PostgreSQL addon
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

3. Set environment variables
```bash
heroku config:set ENVIRONMENT=production
```

4. Deploy
```bash
git push heroku main
```

## Monitoring

### Health Checks

- API Health: `http://localhost:8000/health`
- Detailed Health: `http://localhost:8000/api/v1/stats/health`

### Logs

- Application logs: `logs/app_*.log`
- Error logs: `logs/errors_*.log`

### Metrics

The API exposes Prometheus metrics at `/metrics` (if enabled).

## Scaling

### Horizontal Scaling

1. **Multiple API instances** behind load balancer
2. **Multiple Celery workers** for parallel processing
3. **Separate database** server (PostgreSQL)
4. **Redis cluster** for distributed task queue

### Vertical Scaling

- Increase `MAX_CONCURRENT_DOWNLOADS` in `.env`
- Allocate more CPU/RAM to containers
- Use faster storage for downloads

## Backup

### Database Backup

```bash
# SQLite
cp tiktok_scraper.db tiktok_scraper.db.backup

# PostgreSQL
pg_dump -U tiktok tiktok_scraper > backup.sql
```

### Google Drive

Videos are stored in Google Drive and automatically backed up by Google.

## Security

1. **Use strong API keys** in production
2. **Enable HTTPS** with SSL certificates
3. **Restrict CORS** origins in production
4. **Secure credentials** directory permissions
5. **Use environment variables** for secrets
6. **Regular updates** of dependencies

## Troubleshooting

### Scraping Fails

- Check if TikTok changed their structure
- Enable Playwright fallback
- Use proxy if IP is blocked
- Reduce rate limits

### Google Drive Upload Fails

- Verify OAuth credentials
- Check token expiration
- Ensure sufficient storage space
- Check folder permissions

### Database Errors

- Check database connection
- Verify migrations are applied
- Check disk space

### Performance Issues

- Monitor CPU/RAM usage
- Check database query performance
- Reduce concurrent downloads
- Use caching for API responses
