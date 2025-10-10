import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from app.models.database import AsyncSessionLocal
from app.models.models import ScheduledJob, Job, JobStatus
from app.workers.job_processor import JobProcessor
from app.core.config import settings
from app.core.logging import log
import uuid


class JobScheduler:
    """Manage scheduled recurring jobs"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running = False
    
    async def start(self):
        """Start the scheduler"""
        if not settings.SCHEDULER_ENABLED:
            log.info("Scheduler is disabled in settings")
            return
        
        log.info("Starting job scheduler")
        
        # Load scheduled jobs from database
        await self._load_scheduled_jobs()
        
        # Start the scheduler
        self.scheduler.start()
        self.running = True
        
        log.info("Job scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        if self.running:
            log.info("Stopping job scheduler")
            self.scheduler.shutdown()
            self.running = False
            log.info("Job scheduler stopped")
    
    async def _load_scheduled_jobs(self):
        """Load all enabled scheduled jobs from database"""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ScheduledJob).where(ScheduledJob.enabled == True)
            )
            scheduled_jobs = result.scalars().all()
            
            for scheduled_job in scheduled_jobs:
                await self._add_job_to_scheduler(scheduled_job)
            
            log.info(f"Loaded {len(scheduled_jobs)} scheduled jobs")
    
    async def _add_job_to_scheduler(self, scheduled_job: ScheduledJob):
        """Add a scheduled job to the APScheduler"""
        try:
            # Remove existing job if present
            if self.scheduler.get_job(scheduled_job.id):
                self.scheduler.remove_job(scheduled_job.id)
            
            # Add job with interval trigger
            self.scheduler.add_job(
                func=self._execute_scheduled_job,
                trigger=IntervalTrigger(minutes=scheduled_job.interval_minutes),
                id=scheduled_job.id,
                args=[scheduled_job.id],
                name=scheduled_job.name,
                replace_existing=True
            )
            
            log.info(f"Added scheduled job {scheduled_job.id} ({scheduled_job.name}) "
                    f"with interval {scheduled_job.interval_minutes} minutes")
            
        except Exception as e:
            log.error(f"Error adding scheduled job {scheduled_job.id}: {str(e)}")
    
    async def _execute_scheduled_job(self, scheduled_job_id: str):
        """Execute a scheduled job"""
        log.info(f"Executing scheduled job {scheduled_job_id}")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get scheduled job
                result = await db.execute(
                    select(ScheduledJob).where(ScheduledJob.id == scheduled_job_id)
                )
                scheduled_job = result.scalar_one_or_none()
                
                if not scheduled_job:
                    log.error(f"Scheduled job {scheduled_job_id} not found")
                    return
                
                if not scheduled_job.enabled:
                    log.info(f"Scheduled job {scheduled_job_id} is disabled, skipping")
                    return
                
                # Create a new job
                job = Job(
                    id=str(uuid.uuid4()),
                    mode=scheduled_job.mode,
                    value=scheduled_job.value,
                    limit=scheduled_job.limit,
                    no_watermark=scheduled_job.no_watermark,
                    drive_folder_id=scheduled_job.drive_folder_id,
                    status=JobStatus.PENDING.value
                )
                
                db.add(job)
                await db.commit()
                
                log.info(f"Created job {job.id} from scheduled job {scheduled_job_id}")
                
                # Process the job
                processor = JobProcessor(db)
                await processor.process_job(job.id)
                
                # Update scheduled job statistics
                scheduled_job.last_run_at = datetime.utcnow()
                scheduled_job.next_run_at = datetime.utcnow() + timedelta(minutes=scheduled_job.interval_minutes)
                scheduled_job.total_runs += 1
                
                # Check if job succeeded
                await db.refresh(job)
                if job.status == JobStatus.COMPLETED.value:
                    scheduled_job.successful_runs += 1
                else:
                    scheduled_job.failed_runs += 1
                
                await db.commit()
                
                log.info(f"Scheduled job {scheduled_job_id} execution completed")
                
            except Exception as e:
                log.error(f"Error executing scheduled job {scheduled_job_id}: {str(e)}")
                
                # Update failed runs
                try:
                    result = await db.execute(
                        select(ScheduledJob).where(ScheduledJob.id == scheduled_job_id)
                    )
                    scheduled_job = result.scalar_one_or_none()
                    if scheduled_job:
                        scheduled_job.failed_runs += 1
                        scheduled_job.last_run_at = datetime.utcnow()
                        await db.commit()
                except:
                    pass
    
    async def add_scheduled_job(self, scheduled_job: ScheduledJob):
        """Add a new scheduled job to the scheduler"""
        if self.running and scheduled_job.enabled:
            await self._add_job_to_scheduler(scheduled_job)
    
    async def remove_scheduled_job(self, scheduled_job_id: str):
        """Remove a scheduled job from the scheduler"""
        if self.running:
            try:
                self.scheduler.remove_job(scheduled_job_id)
                log.info(f"Removed scheduled job {scheduled_job_id}")
            except Exception as e:
                log.error(f"Error removing scheduled job {scheduled_job_id}: {str(e)}")
    
    async def update_scheduled_job(self, scheduled_job: ScheduledJob):
        """Update a scheduled job in the scheduler"""
        await self.remove_scheduled_job(scheduled_job.id)
        if scheduled_job.enabled:
            await self.add_scheduled_job(scheduled_job)


# Global scheduler instance
scheduler = JobScheduler()
