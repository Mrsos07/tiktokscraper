from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.models import Job, Video, ScheduledJob, JobStatus, VideoStatus
from app.models.schemas import SystemStats, HealthCheck
from app.core.config import settings
from app.core.logging import log

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("", response_model=SystemStats)
async def get_system_stats(db: AsyncSession = Depends(get_db)):
    """
    Get overall system statistics
    """
    try:
        # Job statistics
        total_jobs_result = await db.execute(select(func.count(Job.id)))
        total_jobs = total_jobs_result.scalar()
        
        pending_jobs_result = await db.execute(
            select(func.count(Job.id)).where(Job.status == JobStatus.PENDING.value)
        )
        pending_jobs = pending_jobs_result.scalar()
        
        running_jobs_result = await db.execute(
            select(func.count(Job.id)).where(Job.status == JobStatus.RUNNING.value)
        )
        running_jobs = running_jobs_result.scalar()
        
        completed_jobs_result = await db.execute(
            select(func.count(Job.id)).where(Job.status == JobStatus.COMPLETED.value)
        )
        completed_jobs = completed_jobs_result.scalar()
        
        failed_jobs_result = await db.execute(
            select(func.count(Job.id)).where(Job.status == JobStatus.FAILED.value)
        )
        failed_jobs = failed_jobs_result.scalar()
        
        # Video statistics
        total_videos_result = await db.execute(select(func.count(Video.id)))
        total_videos = total_videos_result.scalar()
        
        downloaded_videos_result = await db.execute(
            select(func.count(Video.id)).where(Video.status == VideoStatus.DOWNLOADED.value)
        )
        downloaded_videos = downloaded_videos_result.scalar()
        
        uploaded_videos_result = await db.execute(
            select(func.count(Video.id)).where(Video.status == VideoStatus.UPLOADED.value)
        )
        uploaded_videos = uploaded_videos_result.scalar()
        
        failed_videos_result = await db.execute(
            select(func.count(Video.id)).where(Video.status == VideoStatus.FAILED.value)
        )
        failed_videos = failed_videos_result.scalar()
        
        # Storage statistics
        total_storage_result = await db.execute(
            select(func.sum(Video.file_size)).where(Video.file_size.isnot(None))
        )
        total_storage = total_storage_result.scalar() or 0
        
        # Scheduled jobs
        scheduled_jobs_result = await db.execute(select(func.count(ScheduledJob.id)))
        scheduled_jobs_count = scheduled_jobs_result.scalar()
        
        active_scheduled_result = await db.execute(
            select(func.count(ScheduledJob.id)).where(ScheduledJob.enabled == True)
        )
        active_scheduled_jobs = active_scheduled_result.scalar()
        
        return SystemStats(
            total_jobs=total_jobs,
            pending_jobs=pending_jobs,
            running_jobs=running_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            total_videos=total_videos,
            downloaded_videos=downloaded_videos,
            uploaded_videos=uploaded_videos,
            failed_videos=failed_videos,
            total_storage_bytes=total_storage,
            scheduled_jobs_count=scheduled_jobs_count,
            active_scheduled_jobs=active_scheduled_jobs
        )
        
    except Exception as e:
        log.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthCheck)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint
    """
    try:
        # Check database
        db_healthy = True
        try:
            await db.execute(select(1))
        except:
            db_healthy = False
        
        # Check Google Drive
        drive_healthy = True
        try:
            from app.storage.google_drive import GoogleDriveManager
            from pathlib import Path
            
            creds_file = Path(settings.GOOGLE_DRIVE_CREDENTIALS_FILE)
            if not creds_file.exists():
                drive_healthy = False
        except:
            drive_healthy = False
        
        # Check scheduler
        scheduler_healthy = settings.SCHEDULER_ENABLED
        
        return HealthCheck(
            status="healthy" if all([db_healthy, drive_healthy]) else "degraded",
            version=settings.APP_VERSION,
            database=db_healthy,
            google_drive=drive_healthy,
            scheduler=scheduler_healthy
        )
        
    except Exception as e:
        log.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
