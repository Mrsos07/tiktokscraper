"""
YT-DLP Scraper - Most reliable method
"""
import yt_dlp
from pathlib import Path
from typing import List, Dict
from app.core.logging import log


def scrape_and_download_sync(username: str, limit: int = 1, output_dir: Path = None, is_hashtag: bool = False) -> List[Dict]:
    """
    Use yt-dlp to download TikTok videos - WORKS PERFECTLY
    """
    username = username.lstrip('@').lstrip('#')
    
    if is_hashtag or username.startswith('tag/'):
        # Handle hashtag
        import urllib.parse
        if username.startswith('tag/'):
            hashtag = username.replace('tag/', '')
        else:
            hashtag = username
        # URL encode hashtag (important for Arabic/special characters)
        encoded_hashtag = urllib.parse.quote(hashtag)
        url = f"https://www.tiktok.com/tag/{encoded_hashtag}"
        log.info(f"🎯 Using yt-dlp for #{hashtag}")
    else:
        # Handle profile
        url = f"https://www.tiktok.com/@{username}"
        log.info(f"🎯 Using yt-dlp for @{username}")
    
    if not output_dir:
        if is_hashtag:
            output_dir = Path("downloads/hashtag") / hashtag
        else:
            output_dir = Path("downloads/profile") / username
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': str(output_dir / '%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'playlistend': limit,
        'noplaylist': False,
        'cookiefile': None,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            log.info("📥 Downloading with yt-dlp...")
            info = ydl.extract_info(url, download=True)
            
            if not info:
                log.warning("⚠️ No info returned")
                return []
            
            # Handle playlist (profile)
            entries = info.get('entries', [info])
            
            results = []
            for entry in entries[:limit]:
                video_id = entry.get('id')
                video_url = entry.get('webpage_url') or f"https://www.tiktok.com/@{username}/video/{video_id}"
                
                # Find downloaded file
                file_path = None
                for ext in ['mp4', 'webm', 'mkv']:
                    potential_file = output_dir / f"{video_id}.{ext}"
                    if potential_file.exists():
                        file_path = str(potential_file)
                        break
                
                success = file_path is not None
                
                if success:
                    log.info(f"✅ Downloaded: {video_id}")
                    
                    # Generate Arabic subtitle (requires ffmpeg)
                    subtitle_file = None
                    video_with_subtitle = None
                    try:
                        import shutil
                        if shutil.which('ffmpeg'):
                            from app.utils.subtitle_generator import generate_arabic_subtitle, embed_subtitle
                            
                            subtitle_path = generate_arabic_subtitle(Path(file_path))
                            
                            if subtitle_path and subtitle_path.exists():
                                subtitle_file = str(subtitle_path)
                                # Create version with embedded subtitle
                                output_with_sub = Path(file_path).parent / f"{video_id}_ar.mp4"
                                if embed_subtitle(Path(file_path), subtitle_path, output_with_sub):
                                    log.info(f"   ✅ Created version with Arabic subtitle")
                                    video_with_subtitle = str(output_with_sub)
                        else:
                            log.info(f"   ℹ️ ffmpeg not found, skipping subtitle generation")
                    except Exception as e:
                        log.warning(f"   ⚠️ Subtitle generation failed: {e}")
                    
                    # Upload to Google Drive
                    try:
                        from app.uploaders.drive_uploader import DriveUploader
                        
                        uploader = DriveUploader()
                        
                        # Upload original video
                        result = uploader.upload_video(Path(file_path))
                        if result.get('success'):
                            log.info(f"   ✅ Uploaded to Google Drive")
                        
                        # Upload version with subtitle if exists
                        if video_with_subtitle:
                            result_sub = uploader.upload_video(Path(video_with_subtitle))
                            if result_sub.get('success'):
                                log.info(f"   ✅ Uploaded subtitle version to Google Drive")
                    except Exception as e:
                        log.warning(f"   ⚠️ Google Drive upload failed: {e}")
                else:
                    log.warning(f"⚠️ File not found: {video_id}")
                
                results.append({
                    'video_id': video_id,
                    'url': video_url,
                    'success': success,
                    'file_path': file_path,
                    'author_username': username,
                })
            
            log.info(f"✅ Completed: {sum(1 for r in results if r['success'])}/{len(results)} videos")
            return results
            
    except Exception as e:
        log.error(f"❌ yt-dlp error: {e}")
        import traceback
        log.error(traceback.format_exc())
        return []


async def scrape_and_download(username: str, limit: int = 1, output_dir: Path = None, is_hashtag: bool = False) -> List[Dict]:
    """Async wrapper"""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, scrape_and_download_sync, username, limit, output_dir, is_hashtag)
