"""
Auto Scraper - Cron job to check accounts every hour
Monitors accounts and downloads only NEW videos
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select
from app.models.database import get_db
from app.models.models import Job, ScrapingMode, JobStatus, MonitoredAccount, Video, VideoStatus
from app.workers.job_processor import JobProcessor
from app.core.logging import log


class AutoScraper:
    """Automatic scraper that runs periodically"""
    
    def __init__(self):
        self.check_interval = 3600  # 1 hour in seconds
        self.running = False
    
    async def add_account(self, username: str, check_interval_minutes: int = 60):
        """Add account to monitoring list and immediately download latest video"""
        username = username.lstrip('@')
        
        async for db in get_db():
            # Check if already exists
            result = await db.execute(
                select(MonitoredAccount).where(MonitoredAccount.username == username)
            )
            account = result.scalar_one_or_none()
            
            is_new_account = account is None
            
            if account:
                account.enabled = True
                account.check_interval_minutes = check_interval_minutes
                log.info(f"✅ Re-enabled monitoring for @{username}")
            else:
                account = MonitoredAccount(
                    id=str(uuid.uuid4()),
                    username=username,
                    enabled=True,
                    check_interval_minutes=check_interval_minutes
                )
                db.add(account)
                log.info(f"✅ Added @{username} to monitoring (every {check_interval_minutes} min)")
            
            await db.commit()
            await db.refresh(account)
            
            # IMPORTANT: Download latest video immediately for new accounts
            if is_new_account or not account.last_video_id:
                log.info(f"📥 Downloading latest video immediately for @{username}...")
                await self.check_account(account, db)
    
    async def remove_account(self, username: str):
        """Remove account from monitoring"""
        username = username.lstrip('@')
        
        async for db in get_db():
            result = await db.execute(
                select(MonitoredAccount).where(MonitoredAccount.username == username)
            )
            account = result.scalar_one_or_none()
            
            if account:
                account.enabled = False
                await db.commit()
                log.info(f"❌ Disabled monitoring for @{username}")
    
    async def check_account(self, account: MonitoredAccount, db):
        """Check account for new videos - downloads ONLY new videos"""
        try:
            username = account.username
            log.info(f"🔍 Checking @{username} for new videos...")
            
            # Update check time
            account.last_check_at = datetime.utcnow()
            account.total_checks += 1
            
            # Get latest video from profile (limit=1)
            from app.scrapers.profile_scraper import ProfileScraper
            
            async with ProfileScraper() as scraper:
                videos = await scraper.scrape(
                    username=username,
                    limit=1  # Only get the latest video
                )
            
            if not videos:
                log.info(f"   ℹ️ No videos found for @{username}")
                await db.commit()
                return
            
            latest_video = videos[0]
            latest_video_id = latest_video['video_id']
            
            # Check if this is a new video
            if account.last_video_id == latest_video_id:
                log.info(f"   ✅ No new videos (last: {latest_video_id})")
                await db.commit()
                return
            
            # NEW VIDEO FOUND (or first time)!
            if account.last_video_id:
                log.info(f"   🆕 NEW VIDEO FOUND: {latest_video_id}")
                log.info(f"   📥 Downloading and uploading to Google Drive...")
            else:
                log.info(f"   🎬 FIRST VIDEO: {latest_video_id}")
                log.info(f"   📥 Downloading initial video and uploading to Google Drive...")
            
            # Update account tracking
            old_video_id = account.last_video_id
            account.last_video_id = latest_video_id
            account.last_new_video_at = datetime.utcnow()
            account.total_new_videos += 1
            
            # Create job for this new video
            new_job = Job(
                id=str(uuid.uuid4()),
                mode=ScrapingMode.PROFILE.value,
                value=username,
                limit=1,
                no_watermark=True,
                status=JobStatus.PENDING.value
            )
            
            db.add(new_job)
            await db.commit()
            await db.refresh(new_job)
            
            log.info(f"   📝 Created job {new_job.id}")
            
            # Process job (download + upload to Drive)
            processor = JobProcessor(db)
            await processor.process_job(new_job.id)
            
            log.info(f"   ✅ Completed! New video downloaded and uploaded")
            log.info(f"   📊 Stats: {account.total_new_videos} new videos found in {account.total_checks} checks")
            
            await db.commit()
                
        except Exception as e:
            log.error(f"   ❌ Error checking @{username}: {e}")
            import traceback
            log.error(traceback.format_exc())
    
    async def run_check_cycle(self):
        """Run one check cycle for all monitored accounts"""
        async for db in get_db():
            # Get all enabled accounts
            result = await db.execute(
                select(MonitoredAccount).where(MonitoredAccount.enabled == True)
            )
            accounts = result.scalars().all()
            
            if not accounts:
                log.info("📭 No accounts to monitor")
                return
            
            log.info(f"🔄 Starting check cycle for {len(accounts)} accounts")
            
            for account in accounts:
                # Check if it's time to check this account
                if account.last_check_at:
                    time_since_last = datetime.utcnow() - account.last_check_at
                    if time_since_last < timedelta(minutes=account.check_interval_minutes):
                        remaining = account.check_interval_minutes - (time_since_last.seconds // 60)
                        log.info(f"   ⏭️ Skipping @{account.username} (next check in {remaining} min)")
                        continue
                
                await self.check_account(account, db)
                await asyncio.sleep(5)  # Small delay between accounts
            
            log.info("✅ Check cycle completed")
    
    async def start(self):
        """Start the auto scraper"""
        self.running = True
        log.info(f"🚀 Auto Scraper started (checking every {self.check_interval // 60} minutes)")
        
        while self.running:
            try:
                await self.run_check_cycle()
                
                # Wait for next cycle
                log.info(f"⏰ Next check in {self.check_interval // 60} minutes")
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                log.error(f"❌ Error in auto scraper: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def stop(self):
        """Stop the auto scraper"""
        self.running = False
        log.info("🛑 Auto Scraper stopped")


# Global instance
auto_scraper = AutoScraper()
