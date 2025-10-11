import asyncio
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Job, Video, JobStatus, VideoStatus, ScrapingMode
from app.scrapers.profile_scraper import ProfileScraper
from app.scrapers.hashtag_scraper import HashtagScraper
from app.downloaders.video_downloader import VideoDownloader
from app.storage.google_drive import GoogleDriveManager
from app.core.config import settings
from app.core.logging import log


class JobProcessor:
    """Process scraping jobs: scrape, download, and upload to Google Drive"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_DOWNLOADS)
    
    async def process_job(self, job_id: str):
        """
        Process a complete job: scrape -> download -> upload
        
        Args:
            job_id: Job ID to process
        """
        log.info(f"Starting job processing: {job_id}")
        
        try:
            # Get job from database
            result = await self.db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            
            if not job:
                log.error(f"Job not found: {job_id}")
                return
            
            # Update job status
            job.status = JobStatus.RUNNING.value
            job.started_at = datetime.utcnow()
            await self.db.commit()
            
            # Step 1: Scrape videos
            videos_data = await self._scrape_videos(job)
            
            if not videos_data:
                job.status = JobStatus.FAILED.value
                job.error_message = "No videos found"
                job.completed_at = datetime.utcnow()
                await self.db.commit()
                log.warning(f"No videos found for job {job_id}")
                return
            
            job.total_videos = len(videos_data)
            await self.db.commit()
            
            log.info(f"Scraped {len(videos_data)} videos for job {job_id}")
            
            # Step 2: Create video records in database
            await self._create_video_records(job, videos_data)
            
            # Step 3: Download and upload videos
            await self._download_videos(job)
            
            # Step 4: Update job completion
            job.status = JobStatus.COMPLETED.value
            job.completed_at = datetime.utcnow()
            await self.db.commit()
            
            log.info(f"Job {job_id} completed successfully. "
                    f"Success: {job.successful_downloads}, Failed: {job.failed_downloads}")
            
        except Exception as e:
            log.error(f"Error processing job {job_id}: {str(e)}")
            
            # Update job with error
            result = await self.db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                job.status = JobStatus.FAILED.value
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                await self.db.commit()
    
    async def _scrape_videos(self, job: Job) -> List[Dict]:
        """Scrape videos based on job configuration"""
        try:
            if job.mode == ScrapingMode.PROFILE.value or job.mode == "profile":
                async with ProfileScraper() as scraper:
                    videos = await scraper.scrape(
                        username=job.value,
                        limit=job.limit,
                        since=job.since,
                        until=job.until
                    )
            elif job.mode == ScrapingMode.HASHTAG.value or job.mode == "hashtag":
                async with HashtagScraper() as scraper:
                    videos = await scraper.scrape(
                        hashtag=job.value,
                        limit=job.limit,
                        since=job.since,
                        until=job.until
                    )
            elif job.mode == ScrapingMode.EXPLORE.value or job.mode == "explore":
                from app.scrapers.explore_scraper import download_explore_videos
                videos = await download_explore_videos(
                    category=job.value,
                    limit=job.limit
                )
            else:
                raise ValueError(f"Invalid scraping mode: {job.mode}")
            
            return videos
            
        except Exception as e:
            log.error(f"Error scraping videos for job {job.id}: {str(e)}")
            raise
    
    async def _create_video_records(self, job: Job, videos_data: List[Dict]):
        """Create video records in database"""
        for video_data in videos_data:
            try:
                # Check if video already exists
                result = await self.db.execute(
                    select(Video).where(Video.id == video_data['video_id'])
                )
                existing_video = result.scalar_one_or_none()
                
                if existing_video:
                    # If video exists but failed, try again
                    if existing_video.status == VideoStatus.FAILED.value:
                        log.info(f"Video {video_data['video_id']} exists but failed, will retry download")
                        video = existing_video
                        video.job_id = job.id
                        video.status = VideoStatus.PENDING.value
                        video.error_message = None
                        await self.db.commit()
                    # If video exists and uploaded to Drive, skip completely
                    elif existing_video.drive_file_id:
                        log.info(f"Video {video_data['video_id']} already uploaded to Drive, skipping")
                        continue
                    # If video downloaded but not uploaded, will be handled in download phase
                    else:
                        log.info(f"Video {video_data['video_id']} exists but not uploaded, will process")
                        continue
                else:
                    # Parse created_at
                    created_at_tiktok = None
                    if video_data.get('created_at'):
                        if isinstance(video_data['created_at'], (int, float)):
                            created_at_tiktok = datetime.fromtimestamp(video_data['created_at'])
                        elif isinstance(video_data['created_at'], str):
                            try:
                                created_at_tiktok = datetime.fromisoformat(
                                    video_data['created_at'].replace('Z', '+00:00')
                                )
                            except:
                                pass
                    
                    # Create video record
                    video = Video(
                        id=video_data['video_id'],
                        job_id=job.id,
                        url=video_data['url'],
                        desc=video_data.get('desc'),
                        author_username=video_data['author_username'],
                        author_nickname=video_data.get('author_nickname'),
                        views=video_data.get('views', 0),
                        likes=video_data.get('likes', 0),
                        comments=video_data.get('comments', 0),
                        shares=video_data.get('shares', 0),
                        created_at_tiktok=created_at_tiktok,
                        hashtags=video_data.get('hashtags', []),
                        music_title=video_data.get('music_title'),
                        music_author=video_data.get('music_author'),
                        video_url=video_data.get('video_url'),
                        duration=video_data.get('duration'),
                        status=VideoStatus.PENDING.value,
                        raw_metadata=video_data.get('raw_data')
                    )
                    
                    self.db.add(video)
            except Exception as e:
                log.error(f"Error creating video record: {str(e)}")
        
        await self.db.commit()
    
    async def _download_videos(self, job: Job):
        """Download all pending videos for a job"""
        # Get pending videos
        result = await self.db.execute(
            select(Video).where(
                Video.job_id == job.id,
                Video.status == VideoStatus.PENDING.value
            )
        )
        videos = result.scalars().all()
        
        if not videos:
            log.info(f"No pending videos to download for job {job.id}")
            return
        
        log.info(f"Processing {len(videos)} videos for job {job.id}")
        
        # Check if videos are already downloaded (from WorkingScraper)
        for video in videos:
            try:
                # Skip if already uploaded to Drive
                if video.drive_file_id:
                    log.info(f"Video {video.id} already uploaded to Drive, skipping")
                    continue
                
                # If video_url is a local file path, video is already downloaded
                if video.video_url and Path(video.video_url).exists():
                    log.info(f"Video {video.id} already downloaded by WorkingScraper")
                    video.status = VideoStatus.DOWNLOADED.value
                    video.local_path = video.video_url
                    video.file_size = Path(video.video_url).stat().st_size
                    video.has_watermark = False
                    await self.db.commit()
                    
                    # Upload to Google Drive
                    try:
                        from app.uploaders.drive_uploader import DriveUploader
                        
                        video.status = VideoStatus.UPLOADING.value
                        await self.db.commit()
                        
                        uploader = DriveUploader()
                        video_path = Path(video.video_url)
                        
                        # Upload original video
                        upload_result = uploader.upload_video(video_path)
                        
                        if upload_result.get('success'):
                            video.status = VideoStatus.UPLOADED.value
                            video.drive_file_id = upload_result.get('file_id')
                            log.info(f"✅ Uploaded original to Drive: {upload_result.get('web_link')}")
                            
                            # Generate and upload subtitled version
                            try:
                                from app.utils.subtitle_generator import generate_arabic_subtitle, embed_subtitle
                                
                                log.info(f"🎬 Generating Arabic subtitle for {video.id}...")
                                subtitle_path = generate_arabic_subtitle(video_path)
                                
                                if subtitle_path and subtitle_path.exists():
                                    # Create output path for subtitled video
                                    subtitled_video_path = video_path.parent / f"{video.id}_subtitled.mp4"
                                    
                                    if embed_subtitle(video_path, subtitle_path, subtitled_video_path):
                                        # Upload subtitled version
                                        subtitled_upload = uploader.upload_video(subtitled_video_path)
                                        
                                        if subtitled_upload.get('success'):
                                            log.info(f"✅ Uploaded subtitled version to Drive: {subtitled_upload.get('web_link')}")
                                        
                                        # Clean up subtitled video
                                        subtitled_video_path.unlink(missing_ok=True)
                                    
                                    # Clean up subtitle file
                                    subtitle_path.unlink(missing_ok=True)
                                else:
                                    log.info(f"ℹ️ No subtitle generated for {video.id}")
                            except Exception as e:
                                log.warning(f"⚠️ Subtitle generation/upload error: {e}")
                        else:
                            video.status = VideoStatus.DOWNLOADED.value
                            log.warning(f"⚠️ Drive upload failed: {upload_result.get('error')}")
                        
                        await self.db.commit()
                        
                        # Update job progress
                        job.successful_downloads += 1
                        job.progress = int((job.successful_downloads + job.failed_downloads) / job.total_videos * 100)
                        await self.db.commit()
                        
                    except Exception as e:
                        log.warning(f"⚠️ Drive upload error: {e}")
                        video.status = VideoStatus.DOWNLOADED.value
                        await self.db.commit()
                        
                        job.successful_downloads += 1
                        await self.db.commit()
                    
                    continue
                
                # Otherwise, download using VideoDownloader
                # Determine output path
                if job.mode == ScrapingMode.PROFILE.value:
                    output_dir = Path(settings.LOCAL_STORAGE_PATH) / "profile" / job.value
                else:
                    output_dir = Path(settings.LOCAL_STORAGE_PATH) / "hashtag" / job.value
                
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"{video.id}.mp4"
                if not video.video_url:
                    log.warning(f"Video {video.id} has no video_url, attempting to extract from page")
                
                # Download video
                async with VideoDownloader() as downloader:
                    video_data = {
                        'video_id': video.id,
                        'url': video.url,
                        'video_url': video.video_url
                    }
                    
                    log.info(f"Downloading video {video.id} from: {video.video_url[:50] if video.video_url else 'page extraction'}")
                    
                    result = await downloader.download_video(
                        video_data,
                        output_path,
                        no_watermark=job.no_watermark
                    )
                
                if not result['success']:
                    error_msg = result.get('error', 'Download failed')
                    video.status = VideoStatus.FAILED.value
                    video.error_message = error_msg
                    await self.db.commit()
                    
                    job.failed_downloads += 1
                    await self.db.commit()
                    
                    log.error(f"Failed to download video {video.id}: {error_msg}")
                    continue
                
                # Verify file was actually saved
                if not output_path.exists() or output_path.stat().st_size == 0:
                    error_msg = "File not saved or empty after download"
                    video.status = VideoStatus.FAILED.value
                    video.error_message = error_msg
                    await self.db.commit()
                    
                    job.failed_downloads += 1
                    await self.db.commit()
                    
                    log.error(f"Failed to save video {video.id}: {error_msg}")
                    return
                
                # Update video with download info
                video.status = VideoStatus.DOWNLOADED.value
                video.local_path = str(output_path)
                video.file_size = result.get('file_size', 0)
                video.has_watermark = result.get('has_watermark', True)
                await self.db.commit()
                
                log.info(f"Downloaded video {video.id}")
                
                # Upload to Google Drive
                try:
                    from app.uploaders.drive_uploader import DriveUploader
                    
                    video.status = VideoStatus.UPLOADING.value
                    await self.db.commit()
                    
                    uploader = DriveUploader()
                    video_path = Path(video.local_path)
                    
                    # Upload original video
                    upload_result = uploader.upload_video(video_path)
                    
                    if upload_result.get('success'):
                        video.status = VideoStatus.UPLOADED.value
                        video.drive_file_id = upload_result.get('file_id')
                        log.info(f"✅ Uploaded original to Drive: {upload_result.get('web_link')}")
                        
                        # Generate and upload subtitled version
                        try:
                            from app.utils.subtitle_generator import generate_arabic_subtitle, embed_subtitle
                            
                            log.info(f"🎬 Generating Arabic subtitle for {video.id}...")
                            subtitle_path = generate_arabic_subtitle(video_path)
                            
                            if subtitle_path and subtitle_path.exists():
                                # Create output path for subtitled video
                                subtitled_video_path = video_path.parent / f"{video.id}_subtitled.mp4"
                                
                                if embed_subtitle(video_path, subtitle_path, subtitled_video_path):
                                    # Upload subtitled version
                                    subtitled_upload = uploader.upload_video(subtitled_video_path)
                                    
                                    if subtitled_upload.get('success'):
                                        log.info(f"✅ Uploaded subtitled version to Drive: {subtitled_upload.get('web_link')}")
                                    
                                    # Clean up subtitled video
                                    subtitled_video_path.unlink(missing_ok=True)
                                
                                # Clean up subtitle file
                                subtitle_path.unlink(missing_ok=True)
                            else:
                                log.info(f"ℹ️ No subtitle generated for {video.id}")
                        except Exception as e:
                            log.warning(f"⚠️ Subtitle generation/upload error: {e}")
                    else:
                        video.status = VideoStatus.DOWNLOADED.value
                        log.warning(f"⚠️ Drive upload failed: {upload_result.get('error')}")
                    
                    await self.db.commit()
                except Exception as e:
                    log.warning(f"⚠️ Drive upload error: {e}")
                    video.status = VideoStatus.DOWNLOADED.value
                    await self.db.commit()
                
                # Update job progress
                job.successful_downloads += 1
                job.progress = int((job.successful_downloads + job.failed_downloads) / job.total_videos * 100)
                await self.db.commit()
                
                # Keep local file for download endpoint (don't delete)
                # Files will be cleaned up by a separate cleanup task if needed
                log.info(f"Successfully processed video {video.id} - File kept at: {output_path}")
                
            except Exception as e:
                log.error(f"Error processing video {video.id}: {str(e)}")
                
                video.status = VideoStatus.FAILED.value
                video.error_message = str(e)
                await self.db.commit()
                
                job.failed_downloads += 1
                await self.db.commit()
