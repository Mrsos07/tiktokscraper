import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.models import ScheduledJob
from app.models.schemas import ScheduledJobCreate, ScheduledJobResponse
from app.core.logging import log

router = APIRouter(prefix="/scheduled-jobs", tags=["Scheduled Jobs"])


@router.post("", response_model=ScheduledJobResponse, status_code=201)
async def create_scheduled_job(
    job_data: ScheduledJobCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new scheduled job that runs periodically
    """
    try:
        scheduled_job = ScheduledJob(
            id=str(uuid.uuid4()),
            name=job_data.name,
            mode=job_data.mode,
            value=job_data.value,
            limit=job_data.limit,
            no_watermark=job_data.no_watermark,
            drive_folder_id=job_data.drive_folder_id,
            interval_minutes=job_data.interval_minutes,
            enabled=job_data.enabled
        )
        
        db.add(scheduled_job)
        await db.commit()
        await db.refresh(scheduled_job)
        
        log.info(f"Created scheduled job {scheduled_job.id}: {scheduled_job.name}")
        
        return scheduled_job
        
    except Exception as e:
        log.error(f"Error creating scheduled job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[ScheduledJobResponse])
async def list_scheduled_jobs(
    enabled: bool = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all scheduled jobs
    """
    try:
        query = select(ScheduledJob).order_by(ScheduledJob.created_at.desc())
        
        if enabled is not None:
            query = query.where(ScheduledJob.enabled == enabled)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return jobs
        
    except Exception as e:
        log.error(f"Error listing scheduled jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}", response_model=ScheduledJobResponse)
async def get_scheduled_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific scheduled job
    """
    try:
        result = await db.execute(select(ScheduledJob).where(ScheduledJob.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Scheduled job not found")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting scheduled job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{job_id}", response_model=ScheduledJobResponse)
async def update_scheduled_job(
    job_id: str,
    job_data: ScheduledJobCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a scheduled job
    """
    try:
        result = await db.execute(select(ScheduledJob).where(ScheduledJob.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Scheduled job not found")
        
        # Update fields
        job.name = job_data.name
        job.mode = job_data.mode
        job.value = job_data.value
        job.limit = job_data.limit
        job.no_watermark = job_data.no_watermark
        job.drive_folder_id = job_data.drive_folder_id
        job.interval_minutes = job_data.interval_minutes
        job.enabled = job_data.enabled
        
        await db.commit()
        await db.refresh(job)
        
        log.info(f"Updated scheduled job {job_id}")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating scheduled job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}", status_code=204)
async def delete_scheduled_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a scheduled job
    """
    try:
        result = await db.execute(select(ScheduledJob).where(ScheduledJob.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Scheduled job not found")
        
        await db.delete(job)
        await db.commit()
        
        log.info(f"Deleted scheduled job {job_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting scheduled job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/toggle", response_model=ScheduledJobResponse)
async def toggle_scheduled_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle a scheduled job enabled/disabled
    """
    try:
        result = await db.execute(select(ScheduledJob).where(ScheduledJob.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Scheduled job not found")
        
        job.enabled = not job.enabled
        await db.commit()
        await db.refresh(job)
        
        log.info(f"Toggled scheduled job {job_id} to {'enabled' if job.enabled else 'disabled'}")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error toggling scheduled job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
