"""
Explore Page Scraper - For TikTok Explore categories
"""
from pathlib import Path
from typing import List, Dict
from app.core.logging import log
import yt_dlp
import asyncio


def scrape_explore_category_sync(category: str, limit: int = 5) -> List[str]:
    """
    Scrape video URLs from TikTok Explore category using Selenium
    
    Categories:
    - beauty (الجمال والعناية)
    - fashion (الموضة)
    - food (الطعام)
    - etc.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        
        log.info(f"🌐 Using Selenium for Explore category: {category}")
        
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=options)
        
        # Hide automation flags
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            # Go to explore page
            url = "https://www.tiktok.com/explore"
            log.info(f"   Opening: {url}")
            driver.get(url)
            
            # Wait for page to load
            log.info("   Waiting for page to load...")
            time.sleep(8)
            
            # Save page source for debugging
            page_source = driver.page_source
            log.info(f"   Page loaded, length: {len(page_source)} chars")
            
            # Just scroll and get videos - don't try to click category
            # TikTok Explore shows videos directly
            log.info("   Scrolling to load videos...")
            
            for i in range(8):
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                log.info(f"   Scroll {i+1}/8")
                
                # Try to extract videos after each scroll
                video_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
                if len(video_elements) > 0:
                    log.info(f"   Found {len(video_elements)} video elements so far...")
            
            # Extract video URLs with multiple methods
            log.info("   Extracting video URLs...")
            video_urls = []
            
            # Method 1: Find all links with /video/
            video_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
            log.info(f"   Method 1: Found {len(video_elements)} elements")
            
            for element in video_elements:
                try:
                    href = element.get_attribute('href')
                    if href and '/video/' in href and 'http' in href:
                        video_urls.append(href)
                        log.info(f"      Found: {href}")
                except:
                    continue
            
            # Method 2: Extract from page source with regex
            if not video_urls:
                import re
                log.info("   Method 2: Extracting from page source...")
                pattern = r'https://www\.tiktok\.com/@[\w.-]+/video/\d+'
                found_urls = re.findall(pattern, page_source)
                video_urls.extend(found_urls)
                log.info(f"   Found {len(found_urls)} URLs from regex")
            
            # Remove duplicates
            video_urls = list(set(video_urls))[:limit]
            
            log.info(f"   ✅ Found {len(video_urls)} video URLs")
            
            # Print URLs for debugging
            for i, url in enumerate(video_urls, 1):
                log.info(f"      {i}. {url}")
            
            return video_urls
            
        finally:
            driver.quit()
            
    except Exception as e:
        log.error(f"❌ Selenium error: {e}")
        import traceback
        log.error(traceback.format_exc())
        return []


async def download_explore_videos(category: str, limit: int = 5) -> List[Dict]:
    """
    Download videos from TikTok Explore category
    """
    log.info(f"🎯 Downloading videos from Explore: {category}")
    
    video_urls = []
    
    # Try Selenium first
    try:
        loop = asyncio.get_event_loop()
        video_urls = await loop.run_in_executor(
            None,
            scrape_explore_category_sync,
            category,
            limit
        )
    except Exception as e:
        log.warning(f"⚠️ Selenium failed: {e}")
    
    # Fallback: Use trending scraper
    if not video_urls:
        log.info("   Trying trending scraper as fallback...")
        try:
            from app.scrapers.trending_scraper import get_trending_videos
            video_urls = await get_trending_videos(limit)
        except Exception as e:
            log.warning(f"⚠️ Trending scraper failed: {e}")
    
    if not video_urls:
        log.warning("⚠️ No video URLs found")
        return []
    
    # Download each video
    output_dir = Path("downloads/explore") / category
    output_dir.mkdir(parents=True, exist_ok=True)
    
    videos = []
    
    for url in video_urls:
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
    
    log.info(f"✅ Successfully downloaded {len(videos)} videos from {category}")
    return videos
