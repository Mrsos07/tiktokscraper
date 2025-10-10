"""
Hashtag URL Scraper - User provides video URLs from hashtag manually
This is the most reliable method for hashtags
"""
from pathlib import Path
from typing import List, Dict
from app.core.logging import log
import yt_dlp


async def download_from_urls(video_urls: List[str], hashtag: str, limit: int = 5) -> List[Dict]:
    """
    Download videos from provided URLs
    This is the MOST RELIABLE method - user copies video URLs from TikTok hashtag page
    """
    log.info(f"🎯 Downloading {len(video_urls)} videos for #{hashtag}")
    
    output_dir = Path("downloads/hashtag") / hashtag
    output_dir.mkdir(parents=True, exist_ok=True)
    
    videos = []
    
    for url in video_urls[:limit]:
        try:
            log.info(f"   Downloading: {url}")
            
            # Extract video ID from URL
            import re
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
            log.warning(f"      ⚠️ Failed: {e}")
            continue
    
    log.info(f"✅ Successfully downloaded {len(videos)} videos")
    return videos


def scrape_hashtag_with_selenium(hashtag: str, limit: int = 5) -> List[str]:
    """
    Use Selenium to get video URLs from hashtag page
    Returns list of video URLs
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        import urllib.parse
        
        log.info(f"🌐 Using Selenium for #{hashtag}")
        
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            encoded_hashtag = urllib.parse.quote(hashtag)
            url = f"https://www.tiktok.com/tag/{encoded_hashtag}"
            
            log.info(f"   Opening: {url}")
            driver.get(url)
            
            # Wait for videos to load
            time.sleep(5)
            
            # Scroll to load more videos
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract video URLs
            video_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
            video_urls = []
            
            for element in video_elements:
                href = element.get_attribute('href')
                if href and '/video/' in href:
                    video_urls.append(href)
            
            video_urls = list(set(video_urls))[:limit]
            
            log.info(f"   Found {len(video_urls)} video URLs")
            return video_urls
            
        finally:
            driver.quit()
            
    except Exception as e:
        log.error(f"❌ Selenium error: {e}")
        return []
