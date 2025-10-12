import uuid
import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.models import Job, Video, JobStatus, VideoStatus
from app.models.schemas import (
    JobCreate, JobResponse, JobStatusResponse, VideoResponse,
    VideoQuery, VideoListResponse, ErrorResponse
)
from app.workers.job_processor import JobProcessor
from app.core.logging import log
from app.core.job_queue import job_queue

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new scraping job
    
    The job will be processed in the background and will:
    1. Scrape videos from the specified profile or hashtag
    2. Download videos (with optional no-watermark)
    3. Upload to Google Drive in organized folders
    """
    try:
        # Create job record
        job = Job(
            id=str(uuid.uuid4()),
            mode=job_data.mode.value if hasattr(job_data.mode, 'value') else job_data.mode,
            value=job_data.value,
            limit=job_data.limit,
            no_watermark=job_data.no_watermark,
            since=job_data.since,
            until=job_data.until,
            drive_folder_id=job_data.drive_folder_id,
            status=JobStatus.PENDING.value
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        log.info(f"Created job {job.id}: {job.mode}={job.value}")
        
        # Add job to queue instead of processing immediately
        await job_queue.add_job(job.id, process_job_background, job.id)
        
        # Return job with queue info
        queue_size = job_queue.get_queue_size()
        log.info(f"Job {job.id} added to queue. Queue size: {queue_size}")
        
        return job
        
    except Exception as e:
        log.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed job status including all videos and Drive links
    """
    try:
        # Get job
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get videos
        result = await db.execute(
            select(Video).where(Video.job_id == job_id)
        )
        videos = result.scalars().all()
        
        # Build Drive links
        drive_links = []
        for video in videos:
            if video.drive_file_id:
                drive_links.append({
                    'video_id': video.id,
                    'video_link': f"https://drive.google.com/file/d/{video.drive_file_id}/view",
                    'metadata_link': f"https://drive.google.com/file/d/{video.drive_metadata_file_id}/view" if video.drive_metadata_file_id else None,
                    'folder_path': video.drive_folder_path
                })
        
        return {
            'job': job,
            'videos': videos,
            'drive_links': drive_links
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    status: JobStatus = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List all jobs with optional status filter
    """
    try:
        query = select(Job).order_by(Job.created_at.desc())
        
        if status:
            query = query.where(Job.status == status)
        
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return jobs
        
    except Exception as e:
        log.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a job and all associated videos
    """
    try:
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        await db.delete(job)
        await db.commit()
        
        log.info(f"Deleted job {job_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a running or pending job
    """
    try:
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status not in [JobStatus.PENDING.value, JobStatus.RUNNING.value]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel job with status {job.status}"
            )
        
        job.status = JobStatus.CANCELLED.value
        await db.commit()
        await db.refresh(job)
        
        log.info(f"Cancelled job {job_id}")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error cancelling job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_job_background(job_id: str):
    """Background task to process a job"""
    from app.models.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            processor = JobProcessor(db)
            await processor.process_job(job_id)
        except Exception as e:
            log.error(f"Error in background job processing: {str(e)}")
