"""
Working TikTok Scraper - Simple and Effective
Uses Playwright with visible browser to download videos
"""
import sys
import asyncio
import re
from typing import List, Dict, Optional
from pathlib import Path

# Fix for Python 3.13
if sys.platform == 'win32' and sys.version_info >= (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from playwright.async_api import async_playwright, Browser, Page
from app.core.logging import log


class WorkingScraper:
    """Simple working scraper with visible browser"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        await self.init_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_browser()
    
    async def init_browser(self):
        """Initialize Playwright browser - VISIBLE MODE"""
        try:
            # Critical: Set event loop policy BEFORE any async operations
            if sys.platform == 'win32' and sys.version_info >= (3, 13):
                loop = asyncio.get_event_loop()
                if not isinstance(loop, asyncio.SelectorEventLoop):
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
            
            log.info("🚀 Starting Playwright browser (VISIBLE MODE)...")
            self.playwright = await async_playwright().start()
            
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # VISIBLE
                args=['--start-maximized']
            )
            
            log.info("✅ Browser started successfully")
            
        except Exception as e:
            log.error(f"❌ Browser error: {str(e)}")
            raise
    
    async def close_browser(self):
        """Close browser"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except:
            pass
    
    async def scrape_and_download(
        self,
        username: str,
        limit: int = 1,
        output_dir: Path = None
    ) -> List[Dict]:
        """
        Scrape profile and download videos directly
        
        Args:
            username: TikTok username
            limit: Number of videos to download
            output_dir: Directory to save videos
            
        Returns:
            List of downloaded video info
        """
        username = username.lstrip('@')
        url = f"https://www.tiktok.com/@{username}"
        
        log.info(f"🎯 Target: @{username}")
        log.info(f"📍 URL: {url}")
        log.info(f"🔢 Limit: {limit} videos")
        
        if not output_dir:
            output_dir = Path("downloads/profile") / username
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Create page
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            # Go to profile
            log.info("📄 Loading profile page...")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            log.info("⏳ Waiting for content...")
            await asyncio.sleep(5)
            
            # Extract video links
            log.info("🔍 Extracting video links...")
            video_links = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                    return [...new Set(links.map(a => a.href))].filter(href => href.includes('/video/'));
                }
            """)
            
            if not video_links:
                log.warning("⚠️ No video links found")
                await context.close()
                return []
            
            log.info(f"✅ Found {len(video_links)} videos")
            
            # Download videos
            results = []
            for i, video_link in enumerate(video_links[:limit], 1):
                log.info(f"\n📹 Video {i}/{min(limit, len(video_links))}")
                log.info(f"   URL: {video_link}")
                
                # Extract video ID
                match = re.search(r'/video/(\d+)', video_link)
                if not match:
                    log.warning("   ⚠️ Could not extract video ID")
                    continue
                
                video_id = match.group(1)
                output_file = output_dir / f"{video_id}.mp4"
                
                # Download video
                success = await self._download_video(page, video_link, output_file)
                
                result = {
                    'video_id': video_id,
                    'url': video_link,
                    'success': success,
                    'file_path': str(output_file) if success else None,
                    'author_username': username,
                }
                
                results.append(result)
                
                if success:
                    log.info(f"   ✅ Downloaded: {output_file}")
                else:
                    log.error(f"   ❌ Download failed")
                
                await asyncio.sleep(2)
            
            await context.close()
            
            log.info(f"\n✅ Completed: {sum(1 for r in results if r['success'])}/{len(results)} videos downloaded")
            return results
            
        except Exception as e:
            log.error(f"❌ Error: {str(e)}")
            import traceback
            log.error(traceback.format_exc())
            return []
    
    async def _download_video(self, page: Page, video_url: str, output_file: Path) -> bool:
        """Download single video"""
        try:
            # Navigate to video page
            await page.goto(video_url, wait_until='networkidle', timeout=60000)
            await asyncio.sleep(3)
            
            # Try to get download URL from page
            download_url = await page.evaluate("""
                () => {
                    // Try to find video element
                    const video = document.querySelector('video');
                    if (video && video.src) {
                        return video.src;
                    }
                    
                    // Try to find in page data
                    const scripts = document.querySelectorAll('script');
                    for (const script of scripts) {
                        const text = script.textContent;
                        if (text && text.includes('downloadAddr')) {
                            try {
                                const match = text.match(/"downloadAddr":"([^"]+)"/);
                                if (match) {
                                    return match[1].replace(/\\\\u002F/g, '/');
                                }
                            } catch (e) {}
                        }
                    }
                    
                    return null;
                }
            """)
            
            if not download_url:
                log.warning("   ⚠️ Could not find download URL")
                return False
            
            log.info(f"   📥 Downloading from: {download_url[:80]}...")
            
            # Download using page context
            import httpx
            async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
                response = await client.get(download_url)
                response.raise_for_status()
                
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                log.info(f"   💾 Saved: {file_size / 1024 / 1024:.2f} MB")
                
                return True
            
        except Exception as e:
            log.error(f"   ❌ Download error: {str(e)}")
            return False
