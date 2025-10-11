from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.models import Video, VideoStatus
from app.models.schemas import VideoResponse, VideoQuery, VideoListResponse
from app.workers.job_processor import JobProcessor
from app.core.logging import log
from app.core.config import settings

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.get("", response_model=VideoListResponse)
async def list_videos(
    mode: str = None,
    value: str = None,
    author_username: str = None,
    hashtag: str = None,
    status: VideoStatus = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Query videos with various filters
    
    - **mode**: Filter by scraping mode (profile/hashtag)
    - **value**: Filter by profile username or hashtag
    - **author_username**: Filter by video author
    - **hashtag**: Filter by hashtag in video
    - **status**: Filter by video status
    """
    try:
        # Build query
        query = select(Video)
        
        # Apply filters
        if author_username:
            query = query.where(Video.author_username == author_username)
        
        if hashtag:
            # Search in hashtags JSON array
            query = query.where(Video.hashtags.contains([hashtag]))
        
        if status:
            query = query.where(Video.status == status)
        
        # Join with Job to filter by mode/value
        if mode or value:
            from app.models.models import Job
            query = query.join(Video.job)
            
            if mode:
                query = query.where(Job.mode == mode)
            
            if value:
                query = query.where(Job.value == value)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(Video.scraped_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        videos = result.scalars().all()
        
        return {
            'total': total,
            'videos': videos
        }
        
    except Exception as e:
        log.error(f"Error listing videos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific video
    """
    try:
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return video
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{video_id}/retry", response_model=VideoResponse)
async def retry_video_download(
    video_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Retry downloading and uploading a failed video
    """
    try:
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        if video.status == VideoStatus.UPLOADED:
            raise HTTPException(
                status_code=400,
                detail="Video already uploaded successfully"
            )
        
        # Reset video status
        video.status = VideoStatus.PENDING
        video.error_message = None
        await db.commit()
        await db.refresh(video)
        
        log.info(f"Retrying video {video_id}")
        
        # Process in background
        background_tasks.add_task(retry_video_background, video_id)
        
        return video
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error retrying video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/download")
async def download_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download video file as binary
    Returns the video file for download or streaming
    """
    try:
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Check if video has local path
        if not video.local_path:
            raise HTTPException(
                status_code=404, 
                detail="Video file not available locally. Video may be uploaded to Drive only."
            )
        
        video_path = Path(video.local_path)
        
        # Check if file exists
        if not video_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Video file not found on disk"
            )
        
        # Return file for download
        filename = f"{video.author_username}_{video.id}.mp4"
        
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=filename,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error downloading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/stream")
async def stream_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream video file (for preview in browser)
    """
    try:
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        if not video.local_path:
            raise HTTPException(
                status_code=404,
                detail="Video file not available locally"
            )
        
        video_path = Path(video.local_path)
        
        if not video_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Video file not found on disk"
            )
        
        # Return file for streaming
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            headers={
                "Accept-Ranges": "bytes"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error streaming video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{video_id}", status_code=204)
async def delete_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a video record (does not delete from Google Drive)
    """
    try:
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        await db.delete(video)
        await db.commit()
        
        log.info(f"Deleted video {video_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def retry_video_background(video_id: str):
    """Background task to retry a single video"""
    from app.models.database import AsyncSessionLocal
    from app.models.models import Job
    
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Video).where(Video.id == video_id))
            video = result.scalar_one_or_none()
            
            if not video:
                return
            
            result = await db.execute(select(Job).where(Job.id == video.job_id))
            job = result.scalar_one_or_none()
            
            if not job:
                return
            
            processor = JobProcessor(db)
            await processor._process_single_video(job, video)
            
        except Exception as e:
            log.error(f"Error in background video retry: {str(e)}")
