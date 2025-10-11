"""
Automatic Cleanup Task
Deletes local video files older than 1 day
"""
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import select
from app.models.database import AsyncSessionLocal
from app.models.models import Video, VideoStatus
from app.core.config import settings
from app.core.logging import log


class CleanupTask:
    """Automatic cleanup of old video files"""
    
    def __init__(self):
        self.cleanup_interval = 3600  # Run every hour
        self.max_age_hours = 24  # Keep files for 24 hours
        self.running = False
    
    async def start(self):
        """Start the cleanup task"""
        self.running = True
        log.info(f"🧹 Cleanup task started - will delete files older than {self.max_age_hours} hours")
        
        while self.running:
            try:
                await self.run_cleanup()
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                log.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def stop(self):
        """Stop the cleanup task"""
        self.running = False
        log.info("🧹 Cleanup task stopped")
    
    async def run_cleanup(self):
        """Run cleanup cycle - delete old files"""
        try:
            log.info("🧹 Starting cleanup cycle...")
            
            cutoff_time = datetime.utcnow() - timedelta(hours=self.max_age_hours)
            deleted_count = 0
            freed_space = 0
            
            async with AsyncSessionLocal() as db:
                # Get videos older than cutoff time with local files
                result = await db.execute(
                    select(Video).where(
                        Video.scraped_at < cutoff_time,
                        Video.local_path.isnot(None)
                    )
                )
                videos = result.scalars().all()
                
                log.info(f"Found {len(videos)} videos older than {self.max_age_hours} hours")
                
                for video in videos:
                    try:
                        if video.local_path:
                            video_path = Path(video.local_path)
                            
                            if video_path.exists():
                                # Get file size before deletion
                                file_size = video_path.stat().st_size
                                
                                # Delete the file
                                video_path.unlink()
                                
                                deleted_count += 1
                                freed_space += file_size
                                
                                log.info(f"🗑️ Deleted old video: {video.id} ({file_size / 1024 / 1024:.2f} MB)")
                                
                                # Update database - clear local_path
                                video.local_path = None
                                await db.commit()
                    
                    except Exception as e:
                        log.error(f"Error deleting video {video.id}: {e}")
                        continue
            
            if deleted_count > 0:
                freed_mb = freed_space / 1024 / 1024
                log.info(f"✅ Cleanup complete: Deleted {deleted_count} files, freed {freed_mb:.2f} MB")
            else:
                log.info("✅ Cleanup complete: No old files to delete")
        
        except Exception as e:
            log.error(f"Error in cleanup cycle: {e}")


# Global cleanup task instance
cleanup_task = CleanupTask()
