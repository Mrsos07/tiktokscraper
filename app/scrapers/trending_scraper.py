"""
Trending Videos Scraper - Get trending/popular videos
This is more reliable than Explore categories
"""
from pathlib import Path
from typing import List, Dict
from app.core.logging import log
import yt_dlp
import httpx
import re


async def get_trending_videos(limit: int = 10) -> List[str]:
    """
    Get trending video URLs from TikTok
    Uses multiple methods to find popular videos
    """
    log.info(f"🔥 Getting {limit} trending videos")
    
    video_urls = []
    
    try:
        # Method 1: Scrape from trending page
        url = "https://www.tiktok.com/trending"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url)
            html = response.text
            
            # Extract video URLs with regex
            pattern = r'https://www\.tiktok\.com/@[\w.-]+/video/\d+'
            found_urls = re.findall(pattern, html)
            video_urls.extend(found_urls)
            
            log.info(f"   Found {len(found_urls)} URLs from trending page")
    
    except Exception as e:
        log.warning(f"   Method 1 failed: {e}")
    
    # Remove duplicates
    video_urls = list(set(video_urls))[:limit]
    
    log.info(f"✅ Found {len(video_urls)} trending video URLs")
    return video_urls


async def download_trending_videos(category: str = "trending", limit: int = 5) -> List[Dict]:
    """
    Download trending videos
    """
    log.info(f"🎯 Downloading {limit} trending videos")
    
    # Get video URLs
    video_urls = await get_trending_videos(limit)
    
    if not video_urls:
        log.warning("⚠️ No video URLs found")
        return []
    
    # Download each video
    output_dir = Path("downloads/trending") / category
    output_dir.mkdir(parents=True, exist_ok=True)
    
    videos = []
    
    for url in video_urls:
        try:
            log.info(f"   Downloading: {url}")
            
            # Extract video ID from URL
            video_id_match = re.search(r'/video/(\d+)', url)
            if not video_id_match:
                log.warning(f"   ⚠️ Invalid URL format: {url}")
                continue
            
            video_id = video_id_match.group(1)
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': str(output_dir / f'{video_id}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if info:
                    # Find downloaded file
                    file_path = None
                    for ext in ['mp4', 'webm', 'mkv']:
                        potential_file = output_dir / f"{video_id}.{ext}"
                        if potential_file.exists():
                            file_path = str(potential_file)
                            break
                    
                    if file_path:
                        video_data = {
                            'video_id': video_id,
                            'url': url,
                            'desc': info.get('description', ''),
                            'author_username': info.get('uploader', ''),
                            'author_nickname': info.get('uploader', ''),
                            'views': info.get('view_count', 0),
                            'likes': info.get('like_count', 0),
                            'comments': info.get('comment_count', 0),
                            'shares': 0,
                            'created_at': None,
                            'hashtags': [category],
                            'music_title': None,
                            'music_author': None,
                            'video_url': file_path,
                            'duration': info.get('duration'),
                            'raw_data': {}
                        }
                        videos.append(video_data)
                        log.info(f"      ✅ Downloaded: {video_id}")
        
        except Exception as e:
            log.warning(f"      ⚠️ Failed: {e}")
            continue
    
    log.info(f"✅ Successfully downloaded {len(videos)} trending videos")
    return videos
