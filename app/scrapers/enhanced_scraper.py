"""
Enhanced TikTok Scraper with better success rate
Uses multiple strategies to extract video data
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

from playwright.async_api import async_playwright, Page
from app.core.config import settings
from app.core.logging import log


class EnhancedTikTokScraper:
    """Enhanced scraper with multiple extraction strategies"""
    
    def __init__(self):
        self.browser = None
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
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )
            log.info("✅ Browser initialized")
        except Exception as e:
            log.error(f"❌ Error initializing browser: {str(e)}")
            raise
    
    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def scrape_profile(
        self,
        username: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Scrape videos from a TikTok profile
        
        Args:
            username: TikTok username (without @)
            limit: Maximum number of videos to scrape
            
        Returns:
            List of video data dictionaries
        """
        username = username.lstrip('@')
        url = f"https://www.tiktok.com/@{username}"
        
        log.info(f"🔍 Scraping profile: @{username}")
        log.info(f"   URL: {url}")
        
        try:
            page = await self._create_page()
            
            # Navigate to profile
            log.info("   Navigating to profile...")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Try to extract videos
            videos = await self._extract_videos_from_page(page, limit)
            
            await page.close()
            
            log.info(f"✅ Scraped {len(videos)} videos from @{username}")
            return videos
            
        except Exception as e:
            log.error(f"❌ Error scraping profile @{username}: {str(e)}")
            return []
    
    async def scrape_hashtag(
        self,
        hashtag: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Scrape videos from a TikTok hashtag
        
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
            page = await self._create_page()
            
            # Navigate to hashtag page
            log.info("   Navigating to hashtag page...")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Try to extract videos
            videos = await self._extract_videos_from_page(page, limit)
            
            await page.close()
            
            log.info(f"✅ Scraped {len(videos)} videos from #{hashtag}")
            return videos
            
        except Exception as e:
            log.error(f"❌ Error scraping hashtag #{hashtag}: {str(e)}")
            return []
    
    async def _create_page(self) -> Page:
        """Create a new page with stealth settings"""
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
        )
        
        page = await context.new_page()
        
        # Stealth mode
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        return page
    
    async def _extract_videos_from_page(self, page: Page, limit: int) -> List[Dict]:
        """Extract video data from page"""
        videos = []
        
        try:
            # Strategy 1: Extract from video links in DOM
            log.info("   Strategy 1: Extracting from DOM...")
            video_links = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                    return links.map(link => link.href).filter(href => href.includes('/video/'));
                }
            """)
            
            if video_links:
                log.info(f"   Found {len(video_links)} video links")
                
                for link in video_links[:limit]:
                    # Extract video ID from URL
                    match = re.search(r'/video/(\d+)', link)
                    if match:
                        video_id = match.group(1)
                        
                        # Extract username from URL
                        username_match = re.search(r'@([^/]+)/', link)
                        username = username_match.group(1) if username_match else 'unknown'
                        
                        video_data = {
                            'video_id': video_id,
                            'url': link,
                            'author_username': username,
                            'author_nickname': username,
                            'desc': '',
                            'views': 0,
                            'likes': 0,
                            'comments': 0,
                            'shares': 0,
                            'created_at': None,
                            'hashtags': [],
                            'music_title': None,
                            'music_author': None,
                            'video_url': None,
                            'duration': None,
                            'raw_data': {}
                        }
                        
                        videos.append(video_data)
                        
                        if len(videos) >= limit:
                            break
            
            # Strategy 2: Try to extract from page content
            if not videos:
                log.info("   Strategy 2: Extracting from page content...")
                page_content = await page.content()
                
                # Find video IDs in page content
                video_ids = re.findall(r'"id":"(\d{19})"', page_content)
                
                if video_ids:
                    log.info(f"   Found {len(video_ids)} video IDs in content")
                    
                    for video_id in video_ids[:limit]:
                        video_data = {
                            'video_id': video_id,
                            'url': f"https://www.tiktok.com/video/{video_id}",
                            'author_username': 'unknown',
                            'author_nickname': 'unknown',
                            'desc': '',
                            'views': 0,
                            'likes': 0,
                            'comments': 0,
                            'shares': 0,
                            'created_at': None,
                            'hashtags': [],
                            'music_title': None,
                            'music_author': None,
                            'video_url': None,
                            'duration': None,
                            'raw_data': {}
                        }
                        
                        videos.append(video_data)
            
            # Strategy 3: Scroll and wait for dynamic content
            if not videos:
                log.info("   Strategy 3: Scrolling for dynamic content...")
                for _ in range(3):
                    await page.evaluate('window.scrollBy(0, 1000)')
                    await asyncio.sleep(2)
                
                # Try again after scrolling
                video_links = await page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                        return links.map(link => link.href).filter(href => href.includes('/video/'));
                    }
                """)
                
                if video_links:
                    log.info(f"   Found {len(video_links)} video links after scrolling")
                    
                    for link in video_links[:limit]:
                        match = re.search(r'/video/(\d+)', link)
                        if match:
                            video_id = match.group(1)
                            username_match = re.search(r'@([^/]+)/', link)
                            username = username_match.group(1) if username_match else 'unknown'
                            
                            video_data = {
                                'video_id': video_id,
                                'url': link,
                                'author_username': username,
                                'author_nickname': username,
                                'desc': '',
                                'views': 0,
                                'likes': 0,
                                'comments': 0,
                                'shares': 0,
                                'created_at': None,
                                'hashtags': [],
                                'music_title': None,
                                'music_author': None,
                                'video_url': None,
                                'duration': None,
                                'raw_data': {}
                            }
                            
                            videos.append(video_data)
                            
                            if len(videos) >= limit:
                                break
            
            return videos[:limit]
            
        except Exception as e:
            log.error(f"   Error extracting videos: {str(e)}")
            return videos
