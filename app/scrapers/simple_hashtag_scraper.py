"""
Simple Hashtag Scraper - Uses TikTok unofficial API
"""
import re
import httpx
import json
from pathlib import Path
from typing import List, Dict
from app.core.logging import log


async def scrape_hashtag_simple(hashtag: str, limit: int = 5) -> List[Dict]:
    """
    Scrape hashtag using TikTok's unofficial API endpoint
    """
    hashtag = hashtag.lstrip('#')
    log.info(f"🎯 Simple hashtag scraper for #{hashtag}")
    
    try:
        # Use TikTok's API endpoint directly
        import urllib.parse
        
        # Try multiple methods
        video_ids = []
        
        # Method 1: Try to get from web page with better headers
        try:
            encoded_hashtag = urllib.parse.quote(hashtag)
            url = f"https://www.tiktok.com/tag/{encoded_hashtag}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.tiktok.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
            }
            
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0, http2=True) as client:
                response = await client.get(url)
                html = response.text
                
                # Try multiple patterns
                patterns = [
                    r'/video/(\d{19})',
                    r'"id":"(\d{19})"',
                    r'video/(\d{18,20})',
                ]
                
                for pattern in patterns:
                    found_ids = re.findall(pattern, html)
                    video_ids.extend(found_ids)
                
                video_ids = list(set(video_ids))[:limit * 3]  # Get more to filter
                
                if video_ids:
                    log.info(f"   Found {len(video_ids)} video IDs from page")
        except Exception as e:
            log.warning(f"   Method 1 failed: {e}")
        
        # Method 2: Use known popular videos as fallback (for testing)
        if not video_ids:
            log.warning(f"   ⚠️ No video IDs found, using fallback method")
            # Return empty for now - user should try with English hashtags
            return []
        
        log.info(f"   Found {len(video_ids)} video IDs")
        
        # Download each video individually
        output_dir = Path("downloads/hashtag") / hashtag
        output_dir.mkdir(parents=True, exist_ok=True)
        
        videos = []
        for video_id in video_ids:
            try:
                video_url = f"https://www.tiktok.com/@placeholder/video/{video_id}"
                log.info(f"   Downloading video: {video_id}")
                
                # Use yt-dlp to download single video
                import yt_dlp
                
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': str(output_dir / f'{video_id}.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    
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
                                'url': video_url,
                                'desc': info.get('description', ''),
                                'author_username': info.get('uploader', ''),
                                'author_nickname': info.get('uploader', ''),
                                'views': info.get('view_count', 0),
                                'likes': info.get('like_count', 0),
                                'comments': info.get('comment_count', 0),
                                'shares': 0,
                                'created_at': None,
                                'hashtags': [hashtag],
                                'music_title': None,
                                'music_author': None,
                                'video_url': file_path,
                                'duration': info.get('duration'),
                                'raw_data': {}
                            }
                            videos.append(video_data)
                            log.info(f"      ✅ Downloaded: {video_id}")
                
            except Exception as e:
                log.warning(f"      ⚠️ Failed to download {video_id}: {e}")
                continue
        
        log.info(f"✅ Successfully downloaded {len(videos)} videos from #{hashtag}")
        return videos
        
    except Exception as e:
        log.error(f"❌ Simple hashtag scraper error: {e}")
        import traceback
        log.error(traceback.format_exc())
        return []
