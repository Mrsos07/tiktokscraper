from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.database import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoStatus(str, enum.Enum):
    """Video download status enumeration"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    FAILED = "failed"


class ScrapingMode(str, enum.Enum):
    """Scraping mode enumeration"""
    PROFILE = "profile"
    HASHTAG = "hashtag"
    EXPLORE = "explore"


class Job(Base):
    """Job model for tracking scraping tasks"""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True)
    mode = Column(String, nullable=False, index=True)  # Store as string for SQLite compatibility
    value = Column(String, nullable=False, index=True)  # username or hashtag
    limit = Column(Integer, default=50)
    no_watermark = Column(Boolean, default=True)
    since = Column(DateTime, nullable=True)
    until = Column(DateTime, nullable=True)
    drive_folder_id = Column(String, nullable=True)
    
    status = Column(String, default=JobStatus.PENDING.value, index=True)  # Store as string
    progress = Column(Integer, default=0)
    total_videos = Column(Integer, default=0)
    successful_downloads = Column(Integer, default=0)
    failed_downloads = Column(Integer, default=0)
    
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    videos = relationship("Video", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job {self.id} - {self.mode}:{self.value} - {self.status}>"


class Video(Base):
    """Video model for tracking individual videos"""
    __tablename__ = "videos"
    
    id = Column(String, primary_key=True, index=True)  # TikTok video ID
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Video metadata
    url = Column(String, nullable=False)
    desc = Column(Text, nullable=True)
    author_username = Column(String, nullable=False, index=True)
    author_nickname = Column(String, nullable=True)
    
    # Statistics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # Timestamps
    created_at_tiktok = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Content
    hashtags = Column(JSON, default=list)  # List of hashtags
    music_title = Column(String, nullable=True)
    music_author = Column(String, nullable=True)
    
    # Download info
    video_url = Column(String, nullable=True)  # Direct video URL
    has_watermark = Column(Boolean, default=True)
    local_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    duration = Column(Float, nullable=True)  # seconds
    
    # Google Drive info
    drive_file_id = Column(String, nullable=True, index=True)
    drive_folder_path = Column(String, nullable=True)
    drive_metadata_file_id = Column(String, nullable=True)
    
    # Status
    status = Column(String, default=VideoStatus.PENDING.value, index=True)  # Store as string
    download_attempts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Full metadata JSON
    raw_metadata = Column(JSON, nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="videos")
    
    def __repr__(self):
        return f"<Video {self.id} - @{self.author_username} - {self.status}>"
    
    def to_metadata_dict(self) -> dict:
        """Convert to metadata dictionary for JSON export"""
        return {
            "video_id": self.id,
            "desc": self.desc,
            "author": {
                "username": self.author_username,
                "nickname": self.author_nickname,
            },
            "stats": {
                "views": self.views,
                "likes": self.likes,
                "comments": self.comments,
                "shares": self.shares,
            },
            "createdAt": self.created_at_tiktok.isoformat() if self.created_at_tiktok else None,
            "url": self.url,
            "hashtags": self.hashtags or [],
            "music": {
                "title": self.music_title,
                "author": self.music_author,
            },
            "download_info": {
                "has_watermark": self.has_watermark,
                "file_size": self.file_size,
                "duration": self.duration,
            },
            "drive_info": {
                "file_id": self.drive_file_id,
                "folder_path": self.drive_folder_path,
                "metadata_file_id": self.drive_metadata_file_id,
            },
            "scraped_at": self.scraped_at.isoformat(),
        }


class MonitoredAccount(Base):
    """Model for accounts being monitored by Auto Scraper"""
    __tablename__ = "monitored_accounts"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    
    # Tracking
    last_video_id = Column(String, nullable=True)  # ID of last seen video
    last_check_at = Column(DateTime, nullable=True)
    last_new_video_at = Column(DateTime, nullable=True)
    
    # Settings
    enabled = Column(Boolean, default=True, index=True)
    check_interval_minutes = Column(Integer, default=60)
    
    # Stats
    total_checks = Column(Integer, default=0)
    total_new_videos = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<MonitoredAccount @{self.username} - enabled={self.enabled}>"


class ScheduledJob(Base):
    """Model for scheduled recurring jobs"""
    __tablename__ = "scheduled_jobs"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    mode = Column(String, nullable=False)  # Store as string
    value = Column(String, nullable=False)
    limit = Column(Integer, default=50)
    no_watermark = Column(Boolean, default=True)
    drive_folder_id = Column(String, nullable=True)
    
    # Scheduling
    interval_minutes = Column(Integer, default=60)
    enabled = Column(Boolean, default=True, index=True)
    
    # Tracking
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ScheduledJob {self.id} - {self.name} - {'Enabled' if self.enabled else 'Disabled'}>"
