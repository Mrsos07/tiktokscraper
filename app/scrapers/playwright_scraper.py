"""
Playwright-based TikTok scraper for fallback scenarios
"""
import sys
import asyncio
import json
from typing import List, Dict, Optional
from datetime import datetime

# Fix for Python 3.13 on Windows
if sys.platform == 'win32' and sys.version_info >= (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from playwright.async_api import async_playwright, Browser, Page
from app.core.config import settings
from app.core.logging import log


class PlaywrightScraper:
    """Playwright-based scraper for dynamic content"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.init_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_browser()
    
    async def init_browser(self):
        """Initialize Playwright browser"""
        try:
            # Ensure correct event loop policy for Python 3.13 on Windows
            if sys.platform == 'win32' and sys.version_info >= (3, 13):
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            self.playwright = await async_playwright().start()
            
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                ]
            )
            
            log.info("Playwright browser initialized")
            
        except Exception as e:
            log.error(f"Error initializing Playwright: {str(e)}")
            raise
    
    async def close_browser(self):
        """Close Playwright browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        log.info("Playwright browser closed")
    
    async def _create_stealth_page(self) -> Page:
        """Create a page with stealth settings"""
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        page = await context.new_page()
        
        # Add stealth scripts
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            window.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        return page
    
    async def scrape_profile(
        self,
        username: str,
        limit: int = 50,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Dict]:
        """Scrape profile using Playwright"""
        url = f"https://www.tiktok.com/@{username}"
        
        log.info(f"Playwright scraping profile: @{username}")
        
        try:
            page = await self._create_stealth_page()
            
            # Navigate to profile
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await page.wait_for_selector('[data-e2e="user-post-item"]', timeout=10000)
            
            videos = []
            scroll_attempts = 0
            max_scrolls = 20
            
            while len(videos) < limit and scroll_attempts < max_scrolls:
                # Extract video data from page
                page_videos = await self._extract_videos_from_page(page)
                
                for video in page_videos:
                    if video['video_id'] not in [v['video_id'] for v in videos]:
                        if self._filter_video(video, since, until):
                            videos.append(video)
                
                if len(videos) >= limit:
                    break
                
                # Scroll to load more
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(2)
                scroll_attempts += 1
            
            await page.close()
            
            return videos[:limit]
            
        except Exception as e:
            log.error(f"Playwright profile scraping error: {str(e)}")
            return []
    
    async def scrape_hashtag(
        self,
        hashtag: str,
        limit: int = 50,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Dict]:
        """Scrape hashtag using Playwright"""
        url = f"https://www.tiktok.com/tag/{hashtag}"
        
        log.info(f"Playwright scraping hashtag: #{hashtag}")
        
        try:
            page = await self._create_stealth_page()
            
            # Navigate to hashtag page
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await page.wait_for_selector('[data-e2e="challenge-item"]', timeout=10000)
            
            videos = []
            scroll_attempts = 0
            max_scrolls = 20
            
            while len(videos) < limit and scroll_attempts < max_scrolls:
                # Extract video data from page
                page_videos = await self._extract_videos_from_page(page)
                
                for video in page_videos:
                    if video['video_id'] not in [v['video_id'] for v in videos]:
                        if self._filter_video(video, since, until):
                            videos.append(video)
                
                if len(videos) >= limit:
                    break
                
                # Scroll to load more
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(2)
                scroll_attempts += 1
            
            await page.close()
            
            return videos[:limit]
            
        except Exception as e:
            log.error(f"Playwright hashtag scraping error: {str(e)}")
            return []
    
    async def _extract_videos_from_page(self, page: Page) -> List[Dict]:
        """Extract video data from current page state"""
        try:
            # Try to get data from window object
            data = await page.evaluate("""
                () => {
                    const data = window.__UNIVERSAL_DATA_FOR_REHYDRATION__ || 
                                 window.SIGI_STATE || 
                                 window.__DEFAULT_SCOPE__;
                    return data ? JSON.stringify(data) : null;
                }
            """)
            
            if data:
                data = json.loads(data)
                videos = []
                
                # Parse data structure
                if '__DEFAULT_SCOPE__' in data:
                    scope = data['__DEFAULT_SCOPE__']
                    if 'webapp.video-detail' in scope:
                        item = scope['webapp.video-detail'].get('itemInfo', {}).get('itemStruct', {})
                        if item:
                            parsed = self._parse_video_data(item)
                            if parsed:
                                videos.append(parsed)
                
                # Try ItemModule
                if 'ItemModule' in data:
                    for video_id, video_data in data['ItemModule'].items():
                        parsed = self._parse_video_data(video_data)
                        if parsed:
                            videos.append(parsed)
                
                return videos
            
            # Fallback: Parse from DOM
            return await self._extract_videos_from_dom(page)
            
        except Exception as e:
            log.error(f"Error extracting videos from page: {str(e)}")
            return []
    
    async def _extract_videos_from_dom(self, page: Page) -> List[Dict]:
        """Extract video data from DOM elements"""
        try:
            videos = await page.evaluate("""
                () => {
                    const items = document.querySelectorAll('[data-e2e="user-post-item"], [data-e2e="challenge-item"]');
                    const results = [];
                    
                    items.forEach(item => {
                        const link = item.querySelector('a[href*="/video/"]');
                        if (link) {
                            const href = link.getAttribute('href');
                            const match = href.match(/video\\/(\\d+)/);
                            if (match) {
                                results.push({
                                    video_id: match[1],
                                    url: 'https://www.tiktok.com' + href
                                });
                            }
                        }
                    });
                    
                    return results;
                }
            """)
            
            return videos
            
        except Exception as e:
            log.error(f"Error extracting videos from DOM: {str(e)}")
            return []
    
    def _parse_video_data(self, video_data: Dict) -> Optional[Dict]:
        """Parse video data (reuse from base scraper logic)"""
        try:
            video_id = video_data.get('id') or video_data.get('video', {}).get('id')
            
            if not video_id:
                return None
            
            author = video_data.get('author', {})
            author_username = author.get('uniqueId') or author.get('username', 'unknown')
            
            return {
                'video_id': str(video_id),
                'url': f"https://www.tiktok.com/@{author_username}/video/{video_id}",
                'desc': video_data.get('desc', ''),
                'author_username': author_username,
                'author_nickname': author.get('nickname'),
                'views': video_data.get('stats', {}).get('playCount', 0),
                'likes': video_data.get('stats', {}).get('diggCount', 0),
                'comments': video_data.get('stats', {}).get('commentCount', 0),
                'shares': video_data.get('stats', {}).get('shareCount', 0),
                'created_at': video_data.get('createTime'),
                'hashtags': [c.get('title', '').lstrip('#') for c in video_data.get('challenges', [])],
                'music_title': video_data.get('music', {}).get('title'),
                'music_author': video_data.get('music', {}).get('authorName'),
                'video_url': video_data.get('video', {}).get('downloadAddr'),
                'duration': video_data.get('video', {}).get('duration'),
                'raw_data': video_data,
            }
            
        except Exception as e:
            log.error(f"Error parsing video data: {str(e)}")
            return None
    
    def _filter_video(
        self,
        video: Dict,
        since: Optional[datetime],
        until: Optional[datetime]
    ) -> bool:
        """Filter video by date range"""
        if not since and not until:
            return True
        
        created_at = video.get('created_at')
        if not created_at:
            return True
        
        if isinstance(created_at, (int, float)):
            created_at = datetime.fromtimestamp(created_at)
        elif isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                return True
        
        if since and created_at < since:
            return False
        
        if until and created_at > until:
            return False
        
        return True
