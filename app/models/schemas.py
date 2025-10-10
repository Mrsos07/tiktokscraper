from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.models import JobStatus, VideoStatus, ScrapingMode


# Job Schemas
class JobCreate(BaseModel):
    """Schema for creating a new job"""
    mode: ScrapingMode = Field(..., description="Scraping mode: profile or hashtag")
    value: str = Field(..., min_length=1, description="Username (for profile) or tag (for hashtag)")
    limit: int = Field(10, ge=1, le=20, description="Maximum number of videos to scrape (1-20)")
    no_watermark: bool = Field(True, description="Attempt to download without watermark")
    since: Optional[datetime] = Field(None, description="Filter videos created after this date")
    until: Optional[datetime] = Field(None, description="Filter videos created before this date")
    drive_folder_id: Optional[str] = Field(None, description="Google Drive folder ID for uploads")
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v: str, info) -> str:
        """Validate and clean username/hashtag"""
        v = v.strip()
        if info.data.get('mode') == ScrapingMode.PROFILE:
            # Remove @ if present
            v = v.lstrip('@')
        elif info.data.get('mode') == ScrapingMode.HASHTAG:
            # Remove # if present
            v = v.lstrip('#')
        return v


class JobResponse(BaseModel):
    """Schema for job response"""
    id: str
    mode: ScrapingMode
    value: str
    limit: int
    no_watermark: bool
    since: Optional[datetime]
    until: Optional[datetime]
    drive_folder_id: Optional[str]
    status: JobStatus
    progress: int
    total_videos: int
    successful_downloads: int
    failed_downloads: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class JobStatusResponse(BaseModel):
    """Detailed job status with videos"""
    job: JobResponse
    videos: List["VideoResponse"]
    drive_links: List[Dict[str, str]]


# Video Schemas
class VideoResponse(BaseModel):
    """Schema for video response"""
    id: str
    job_id: str
    url: str
    desc: Optional[str]
    author_username: str
    author_nickname: Optional[str]
    views: int
    likes: int
    comments: int
    shares: int
    created_at_tiktok: Optional[datetime]
    scraped_at: datetime
    hashtags: List[str]
    music_title: Optional[str]
    music_author: Optional[str]
    has_watermark: bool
    file_size: Optional[int]
    duration: Optional[float]
    drive_file_id: Optional[str]
    drive_folder_path: Optional[str]
    status: VideoStatus
    error_message: Optional[str]
    
    model_config = {"from_attributes": True}


class VideoQuery(BaseModel):
    """Schema for querying videos"""
    mode: Optional[ScrapingMode] = None
    value: Optional[str] = None
    author_username: Optional[str] = None
    hashtag: Optional[str] = None
    status: Optional[VideoStatus] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)


class VideoListResponse(BaseModel):
    """Schema for video list response"""
    total: int
    videos: List[VideoResponse]


# Scheduled Job Schemas
class ScheduledJobCreate(BaseModel):
    """Schema for creating a scheduled job"""
    name: str = Field(..., min_length=1, max_length=100)
    mode: ScrapingMode
    value: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=20)
    no_watermark: bool = True
    drive_folder_id: Optional[str] = None
    interval_minutes: int = Field(60, ge=5, description="Interval in minutes between runs")
    enabled: bool = True


class ScheduledJobResponse(BaseModel):
    """Schema for scheduled job response"""
    id: str
    name: str
    mode: ScrapingMode
    value: str
    limit: int
    no_watermark: bool
    drive_folder_id: Optional[str]
    interval_minutes: int
    enabled: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    total_runs: int
    successful_runs: int
    failed_runs: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Statistics Schemas
class SystemStats(BaseModel):
    """System statistics"""
    total_jobs: int
    pending_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_videos: int
    downloaded_videos: int
    uploaded_videos: int
    failed_videos: int
    total_storage_bytes: int
    scheduled_jobs_count: int
    active_scheduled_jobs: int


# Error Response
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health Check
class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: bool
    google_drive: bool
    scheduler: bool
