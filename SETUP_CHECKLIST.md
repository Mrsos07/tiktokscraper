# Setup Checklist

Use this checklist to ensure your TikTok Scraper installation is complete and working correctly.

## Pre-Installation

- [ ] Python 3.10 or higher installed
- [ ] Git installed (optional, for cloning)
- [ ] Google account created
- [ ] 2GB+ free disk space available
- [ ] Internet connection stable

## Installation Steps

### 1. Environment Setup
- [ ] Project directory created/cloned
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browser installed (`playwright install chromium`)

### 2. Configuration
- [ ] `.env` file created (copied from `.env.example`)
- [ ] Database URL configured in `.env`
- [ ] Google Drive credentials path set in `.env`
- [ ] Rate limits configured (optional)
- [ ] Proxy settings configured (if needed)

### 3. Google Drive Setup
- [ ] Google Cloud Console project created
- [ ] Google Drive API enabled
- [ ] OAuth 2.0 credentials created (Desktop app)
- [ ] Credentials JSON downloaded to `credentials/` folder
- [ ] Google Drive authentication completed (`python scripts/setup_google_drive.py`)
- [ ] Token file generated successfully

### 4. Database Initialization
- [ ] Database initialized (`python scripts/init_db.py`)
- [ ] Database file created (SQLite) or connection verified (PostgreSQL)
- [ ] No errors in initialization logs

### 5. Testing
- [ ] Scraper test successful (`python scripts/test_scraper.py --mode profile --value khaby.lame --limit 5`)
- [ ] Videos scraped successfully
- [ ] No blocking or rate limit errors

## Service Startup

### API Server
- [ ] API server starts without errors (`uvicorn app.main:app --reload`)
- [ ] API accessible at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Health check returns "healthy" (http://localhost:8000/health)

### Admin Dashboard
- [ ] Streamlit starts without errors (`streamlit run admin/dashboard.py`)
- [ ] Dashboard accessible at http://localhost:8501
- [ ] Dashboard connects to API successfully
- [ ] Statistics display correctly

## Functional Testing

### Job Creation
- [ ] Can create profile scraping job via API
- [ ] Can create hashtag scraping job via API
- [ ] Can create job via admin dashboard
- [ ] Job appears in jobs list
- [ ] Job status updates correctly

### Video Processing
- [ ] Videos are scraped successfully
- [ ] Videos are downloaded to local storage
- [ ] Videos are uploaded to Google Drive
- [ ] Metadata JSON files created
- [ ] Drive links accessible
- [ ] Folder structure correct (`TikTok/{mode}/{value}/{YYYY}/{MM}/`)

### Scheduled Jobs
- [ ] Can create scheduled job
- [ ] Scheduled job appears in list
- [ ] Can enable/disable scheduled job
- [ ] Scheduled job executes at interval (wait for next run)

### API Endpoints
- [ ] `GET /api/v1/stats` returns statistics
- [ ] `GET /api/v1/jobs` lists jobs
- [ ] `GET /api/v1/videos` lists videos
- [ ] `GET /api/v1/scheduled-jobs` lists scheduled jobs
- [ ] All endpoints return valid JSON

### Admin Dashboard
- [ ] Dashboard shows correct statistics
- [ ] Can create jobs from dashboard
- [ ] Can view job details
- [ ] Can view video list
- [ ] Can manage scheduled jobs
- [ ] Refresh button works

## Optional Features

### Docker Deployment
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] `docker-compose up` builds successfully
- [ ] All containers running
- [ ] Services accessible via Docker network

### Proxy Configuration
- [ ] Proxy URL configured in `.env`
- [ ] Proxy connection tested
- [ ] Scraping works through proxy

### External No-Watermark API
- [ ] External API key obtained
- [ ] API key configured in `.env`
- [ ] API URL configured
- [ ] No-watermark downloads working

### PostgreSQL Database
- [ ] PostgreSQL installed/accessible
- [ ] Database created
- [ ] Connection string configured
- [ ] Migrations applied (if using Alembic)

## Troubleshooting Checks

### If Scraping Fails
- [ ] Username/hashtag is correct (no @ or #)
- [ ] Content is public
- [ ] Rate limits not exceeded
- [ ] Playwright fallback enabled
- [ ] Logs checked for errors

### If Downloads Fail
- [ ] Video URL is valid
- [ ] Network connection stable
- [ ] Sufficient disk space
- [ ] Timeout settings adequate
- [ ] Retry logic working

### If Google Drive Upload Fails
- [ ] Credentials file exists
- [ ] Token file valid (not expired)
- [ ] Sufficient Drive storage
- [ ] Folder permissions correct
- [ ] Network connection stable

### If API Errors Occur
- [ ] API server running
- [ ] Database accessible
- [ ] Logs checked for errors
- [ ] Environment variables correct
- [ ] Dependencies installed

### If Dashboard Errors Occur
- [ ] Streamlit running
- [ ] API server accessible
- [ ] API URL correct in dashboard
- [ ] Port not blocked by firewall

## Security Checklist

- [ ] API keys changed from defaults
- [ ] `.env` file not committed to git
- [ ] Credentials folder in `.gitignore`
- [ ] CORS origins restricted (production)
- [ ] HTTPS enabled (production)
- [ ] File permissions secure

## Performance Optimization

- [ ] Rate limits configured appropriately
- [ ] Concurrent downloads set correctly
- [ ] Database indexes created (if needed)
- [ ] Logs rotated regularly
- [ ] Disk space monitored

## Documentation Review

- [ ] README.md read
- [ ] QUICKSTART.md followed
- [ ] API_DOCUMENTATION.md reviewed
- [ ] DEPLOYMENT.md consulted (if deploying)
- [ ] Examples tested

## Final Verification

### Complete System Test
1. [ ] Create a profile scraping job for 5 videos
2. [ ] Wait for job completion
3. [ ] Verify all 5 videos downloaded
4. [ ] Check Google Drive for uploaded files
5. [ ] Verify folder structure is correct
6. [ ] Check metadata JSON files
7. [ ] Verify Drive links work
8. [ ] Check statistics are updated
9. [ ] Review logs for any errors
10. [ ] Confirm no issues

### Production Readiness (if deploying)
- [ ] Environment set to "production"
- [ ] Debug mode disabled
- [ ] Secure secrets configured
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Resource limits set

## Success Criteria

✅ All core features working
✅ No critical errors in logs
✅ Videos successfully uploaded to Drive
✅ API responding correctly
✅ Dashboard functional
✅ Documentation understood

## Getting Help

If you encounter issues:

1. **Check Logs**: Review `logs/app_*.log` and `logs/errors_*.log`
2. **Review Documentation**: Check README.md and troubleshooting sections
3. **Test Components**: Use test scripts to isolate issues
4. **Check Configuration**: Verify `.env` settings
5. **Search Issues**: Look for similar problems in issue tracker
6. **Ask for Help**: Open an issue with detailed information

## Maintenance Tasks

### Daily
- [ ] Monitor logs for errors
- [ ] Check disk space
- [ ] Verify scheduled jobs running

### Weekly
- [ ] Review statistics
- [ ] Clean up old local files
- [ ] Check Google Drive storage
- [ ] Update failed jobs

### Monthly
- [ ] Update dependencies
- [ ] Review and optimize rate limits
- [ ] Backup database
- [ ] Review security settings

---

**Congratulations!** If all items are checked, your TikTok Scraper is fully operational! 🎉

**Next Steps**:
- Start scraping your first videos
- Set up scheduled jobs for automation
- Explore advanced features
- Customize to your needs

**Remember**: Use responsibly and ethically! Respect content creators and platform policies.
