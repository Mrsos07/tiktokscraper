"""
Reliable TikTok Scraper using Playwright
Directly extracts video download URLs without watermark
"""
import sys
import asyncio
import json
import re
from typing import List, Dict, Optional
from datetime import datetime

# Fix for Python 3.13 on Windows
if sys.platform == 'win32' and sys.version_info >= (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from app.core.config import settings
from app.core.logging import log


class ReliableTikTokScraper:
    """Reliable scraper using Playwright to extract video URLs"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        await self.init_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_browser()
    
    async def init_browser(self):
        """Initialize Playwright browser"""
        try:
            # Ensure correct event loop policy for Python 3.13 on Windows
            if sys.platform == 'win32' and sys.version_info >= (3, 13):
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            log.info("🚀 Initializing Playwright browser...")
            self.playwright = await async_playwright().start()
            
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # تم تغييره إلى False لرؤية المتصفح
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            )
            
            log.info("✅ Browser initialized successfully (visible mode)")
            
        except Exception as e:
            log.error(f"❌ Error initializing browser: {str(e)}")
            log.error("💡 Make sure Playwright is installed: playwright install chromium")
            raise
    
    async def close_browser(self):
        """Close browser"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            log.info("Browser closed")
        except Exception as e:
            log.error(f"Error closing browser: {str(e)}")
    
    async def scrape_profile(
        self,
        username: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Scrape videos from TikTok profile
        
        Args:
            username: TikTok username (without @)
            limit: Maximum number of videos to scrape
            
        Returns:
            List of video data dictionaries with download URLs
        """
        username = username.lstrip('@')
        url = f"https://www.tiktok.com/@{username}"
        
        log.info(f"🔍 Scraping profile: @{username}")
        log.info(f"   URL: {url}")
        log.info(f"   Limit: {limit} videos")
        
        try:
            # Create new page
            page = await self._create_stealth_page()
            
            # Navigate to profile
            log.info("   📄 Loading profile page...")
            try:
                await page.goto(url, wait_until='networkidle', timeout=60000)
                log.info("   ✅ Page loaded successfully")
            except Exception as e:
                log.warning(f"   ⚠️ Page load timeout, continuing anyway: {str(e)}")
            
            # Wait for content to load
            log.info("   ⏳ Waiting for content to render...")
            await asyncio.sleep(10)  # زيادة الوقت لرؤية الصفحة
            
            # Try to extract videos
            log.info("   🔎 Extracting video links...")
            video_links = await self._extract_video_links(page, limit)
            
            log.info(f"   📊 Extracted {len(video_links)} video links")
            
            if not video_links:
                log.warning(f"   ⚠️ No video links found on profile page")
                await page.close()
                return []
            
            log.info(f"   ✅ Found {len(video_links)} video links")
            
            # Extract video data for each link
            videos = []
            for i, video_link in enumerate(video_links[:limit], 1):
                log.info(f"   📹 Processing video {i}/{len(video_links[:limit])}: {video_link}")
                
                video_data = await self._extract_video_data(page, video_link, username)
                
                if video_data:
                    videos.append(video_data)
                    log.info(f"      ✅ Video {i} extracted successfully")
                else:
                    log.warning(f"      ⚠️ Failed to extract video {i}")
                
                # Small delay between videos
                await asyncio.sleep(3)  # زيادة الوقت لرؤية كل خطوة
            
            await page.close()
            
            log.info(f"✅ Successfully scraped {len(videos)} videos from @{username}")
            return videos
            
        except Exception as e:
            log.error(f"❌ Error scraping profile @{username}: {str(e)}")
            import traceback
            log.error(traceback.format_exc())
            return []
    
    async def scrape_hashtag(
        self,
        hashtag: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Scrape videos from TikTok hashtag
        
        Args:
            hashtag: Hashtag name (without #)
            limit: Maximum number of videos to scrape
            
        Returns:
            List of video data dictionaries
        """
        hashtag = hashtag.lstrip('#')
        url = f"https://www.tiktok.com/tag/{hashtag}"
        
        log.info(f"🔍 Scraping hashtag: #{hashtag}")
        log.info(f"   URL: {url}")
        
        try:
            page = await self._create_stealth_page()
            
            log.info("   📄 Loading hashtag page...")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            await asyncio.sleep(5)
            
            log.info("   🔎 Extracting video links...")
            video_links = await self._extract_video_links(page, limit)
            
            if not video_links:
                log.warning(f"   ⚠️ No video links found")
                await page.close()
                return []
            
            log.info(f"   ✅ Found {len(video_links)} video links")
            
            videos = []
            for i, video_link in enumerate(video_links[:limit], 1):
                log.info(f"   📹 Processing video {i}/{len(video_links[:limit])}")
                
                video_data = await self._extract_video_data(page, video_link)
                
                if video_data:
                    videos.append(video_data)
                
                await asyncio.sleep(2)
            
            await page.close()
            
            log.info(f"✅ Successfully scraped {len(videos)} videos from #{hashtag}")
            return videos
            
        except Exception as e:
            log.error(f"❌ Error scraping hashtag #{hashtag}: {str(e)}")
            return []
    
    async def _create_stealth_page(self) -> Page:
        """Create a new page with stealth settings"""
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        page = await context.new_page()
        
        # Inject stealth scripts
        await page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        return page
    
    async def _extract_video_links(self, page: Page, limit: int) -> List[str]:
        """Extract video links from page"""
        try:
            # Scroll to load more videos
            for _ in range(3):
                await page.evaluate('window.scrollBy(0, 1000)')
                await asyncio.sleep(2)
            
            # Extract video links
            video_links = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                    const uniqueLinks = [...new Set(links.map(link => link.href))];
                    return uniqueLinks.filter(href => href.includes('/video/'));
                }
            """)
            
            return video_links[:limit]
            
        except Exception as e:
            log.error(f"Error extracting video links: {str(e)}")
            return []
    
    async def _extract_video_data(
        self,
        page: Page,
        video_url: str,
        username: Optional[str] = None
    ) -> Optional[Dict]:
        """Extract video data including download URL"""
        try:
            # Navigate to video page
            await page.goto(video_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)
            
            # Extract video ID from URL
            video_id_match = re.search(r'/video/(\d+)', video_url)
            video_id = video_id_match.group(1) if video_id_match else None
            
            if not video_id:
                log.warning(f"Could not extract video ID from {video_url}")
                return None
            
            # Extract username from URL if not provided
            if not username:
                username_match = re.search(r'@([^/]+)/', video_url)
                username = username_match.group(1) if username_match else 'unknown'
            
            # Get page content
            content = await page.content()
            
            # Try to extract video download URL from page
            download_url = await self._extract_download_url(content, page)
            
            if not download_url:
                log.warning(f"Could not extract download URL for video {video_id}")
            
            # Extract basic metadata
            try:
                title = await page.evaluate("""
                    () => {
                        const meta = document.querySelector('meta[property="og:title"]');
                        return meta ? meta.content : '';
                    }
                """)
            except:
                title = ''
            
            # Build video data
            video_data = {
                'video_id': video_id,
                'url': video_url,
                'desc': title,
                'author_username': username,
                'author_nickname': username,
                'views': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'created_at': None,
                'hashtags': [],
                'music_title': None,
                'music_author': None,
                'video_url': download_url,
                'duration': None,
                'raw_data': {}
            }
            
            return video_data
            
        except Exception as e:
            log.error(f"Error extracting video data: {str(e)}")
            return None
    
    async def _extract_download_url(self, html: str, page: Page) -> Optional[str]:
        """Extract video download URL without watermark"""
        try:
            # Method 1: Extract from SIGI_STATE
            match = re.search(r'<script id="SIGI_STATE"[^>]*>([^<]+)</script>', html)
            if match:
                try:
                    data = json.loads(match.group(1))
                    
                    # Look for video URL in ItemModule
                    if 'ItemModule' in data:
                        for item_id, item_data in data['ItemModule'].items():
                            if isinstance(item_data, dict) and 'video' in item_data:
                                video_info = item_data['video']
                                
                                # Try downloadAddr first (no watermark)
                                for url_field in ['downloadAddr', 'playAddr']:
                                    url_data = video_info.get(url_field)
                                    
                                    if url_data:
                                        if isinstance(url_data, str):
                                            return url_data
                                        elif isinstance(url_data, dict):
                                            url_list = url_data.get('UrlList', [])
                                            if url_list:
                                                return url_list[0]
                except json.JSONDecodeError:
                    pass
            
            # Method 2: Try to intercept network requests
            # This would require setting up request interception before navigation
            
            # Method 3: Extract from __UNIVERSAL_DATA_FOR_REHYDRATION__
            match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>([^<]+)</script>', html)
            if match:
                try:
                    data = json.loads(match.group(1))
                    
                    # Navigate through the data structure
                    if '__DEFAULT_SCOPE__' in data:
                        default_scope = data['__DEFAULT_SCOPE__']
                        
                        # Look for video data
                        if 'webapp.video-detail' in default_scope:
                            video_detail = default_scope['webapp.video-detail']
                            if 'itemInfo' in video_detail:
                                item_info = video_detail['itemInfo']
                                if 'itemStruct' in item_info:
                                    item_struct = item_info['itemStruct']
                                    if 'video' in item_struct:
                                        video_info = item_struct['video']
                                        
                                        for url_field in ['downloadAddr', 'playAddr']:
                                            url_data = video_info.get(url_field)
                                            
                                            if url_data:
                                                if isinstance(url_data, str):
                                                    return url_data
                                                elif isinstance(url_data, dict):
                                                    url_list = url_data.get('UrlList', [])
                                                    if url_list:
                                                        return url_list[0]
                except json.JSONDecodeError:
                    pass
            
            # Method 4: Use regex to find video URLs in HTML
            patterns = [
                r'"downloadAddr":"([^"]+)"',
                r'"playAddr":"([^"]+)"',
                r'"UrlList":\["([^"]+)"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html)
                if matches:
                    url = matches[0]
                    # Unescape URL
                    url = url.encode().decode('unicode_escape')
                    if url.startswith('http'):
                        return url
            
            return None
            
        except Exception as e:
            log.error(f"Error extracting download URL: {str(e)}")
            return None
