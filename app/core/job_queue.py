"""
Job Queue Manager to prevent concurrent TikTok requests
"""
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.core.logging import log


class JobQueue:
    """Manages job execution queue to prevent rate limiting"""
    
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.processing = False
        self.last_request_time: Optional[datetime] = None
        self.min_delay_seconds = 10  # Minimum 10 seconds between jobs
        self.active_jobs: Dict[str, datetime] = {}
        
    async def add_job(self, job_id: str, processor_func, *args, **kwargs):
        """Add job to queue"""
        log.info(f"Adding job {job_id} to queue")
        await self.queue.put((job_id, processor_func, args, kwargs))
        
        # Start processing if not already running
        if not self.processing:
            asyncio.create_task(self._process_queue())
    
    async def _process_queue(self):
        """Process jobs from queue one at a time"""
        if self.processing:
            return
            
        self.processing = True
        log.info("Job queue processor started")
        
        try:
            while not self.queue.empty():
                job_id, processor_func, args, kwargs = await self.queue.get()
                
                try:
                    # Wait minimum delay between jobs
                    if self.last_request_time:
                        elapsed = (datetime.utcnow() - self.last_request_time).total_seconds()
                        if elapsed < self.min_delay_seconds:
                            wait_time = self.min_delay_seconds - elapsed
                            log.info(f"Waiting {wait_time:.1f}s before processing job {job_id}")
                            await asyncio.sleep(wait_time)
                    
                    # Mark job as active
                    self.active_jobs[job_id] = datetime.utcnow()
                    log.info(f"Processing job {job_id} from queue")
                    
                    # Process job
                    await processor_func(*args, **kwargs)
                    
                    # Update last request time
                    self.last_request_time = datetime.utcnow()
                    
                except Exception as e:
                    log.error(f"Error processing job {job_id}: {e}")
                finally:
                    # Remove from active jobs
                    self.active_jobs.pop(job_id, None)
                    self.queue.task_done()
                    
        finally:
            self.processing = False
            log.info("Job queue processor stopped")
    
    def is_job_active(self, job_id: str) -> bool:
        """Check if job is currently being processed"""
        return job_id in self.active_jobs
    
    def get_queue_size(self) -> int:
        """Get number of jobs in queue"""
        return self.queue.qsize()
    
    def get_active_jobs(self) -> Dict[str, datetime]:
        """Get currently active jobs"""
        return self.active_jobs.copy()


# Global job queue instance
job_queue = JobQueue()
