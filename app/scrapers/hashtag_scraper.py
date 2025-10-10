from typing import List, Dict, Optional
from datetime import datetime
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.playwright_scraper import PlaywrightScraper
from app.core.config import settings
from app.core.logging import log


class HashtagScraper(BaseScraper):
    """Scraper for TikTok hashtag pages"""
    
    async def scrape(
        self,
        hashtag: str,
        limit: int = 50,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Scrape videos from a TikTok hashtag page
        
        Args:
            hashtag: Hashtag name (without #)
            limit: Maximum number of videos to scrape
            since: Filter videos created after this date
            until: Filter videos created before this date
            
        Returns:
            List of video data dictionaries
        """
        hashtag = hashtag.lstrip('#')
        url = f"https://www.tiktok.com/tag/{hashtag}"
        
        log.info(f"Starting hashtag scrape for #{hashtag}, limit={limit}")
        
        try:
            # Strategy 1: Selenium Scraper (Most Reliable for hashtags)
            try:
                from app.scrapers.hashtag_url_scraper import scrape_hashtag_with_selenium, download_from_urls
                import asyncio
                
                log.info("🎯 Using Selenium for hashtag...")
                
                # Run Selenium in thread pool
                loop = asyncio.get_event_loop()
                video_urls = await loop.run_in_executor(
                    None,
                    scrape_hashtag_with_selenium,
                    hashtag,
                    limit
                )
                
                if video_urls:
                    log.info(f"   Found {len(video_urls)} URLs, downloading...")
                    videos = await download_from_urls(video_urls, hashtag, limit)
                    
                    if videos:
                        log.info(f"✅ Successfully downloaded {len(videos)} videos")
                        return videos
            except Exception as e:
                log.warning(f"⚠️ Selenium scraper failed: {str(e)}")
                import traceback
                log.error(traceback.format_exc())
            
            # Strategy 2: Direct HTTP request
            log.info("Trying HTTP scraping...")
            videos = await self._scrape_with_http(url, limit, since, until)
            
            if videos:
                log.info(f"✅ Successfully scraped {len(videos)} videos via HTTP")
                return videos
            
            # Strategy 3: Playwright fallback
            if settings.TIKTOK_USE_PLAYWRIGHT_FALLBACK:
                log.info("Trying Playwright fallback...")
                videos = await self._scrape_with_playwright(hashtag, limit, since, until)
                
                if videos:
                    log.info(f"✅ Successfully scraped {len(videos)} videos via Playwright")
                    return videos
            
            log.warning(f"⚠️ No videos found for #{hashtag} using any method")
            return []
            
        except Exception as e:
            log.error(f"❌ Error scraping hashtag #{hashtag}: {str(e)}")
            import traceback
            log.error(traceback.format_exc())
            raise
    
    async def _scrape_with_http(
        self,
        url: str,
        limit: int,
        since: Optional[datetime],
        until: Optional[datetime]
    ) -> List[Dict]:
        """Scrape using direct HTTP requests"""
        try:
            html = await self._fetch_page(url)
            
            # Extract JSON data from script tag
            data = self._extract_json_from_script(html)
            
            if not data:
                log.warning("No JSON data found in page")
                return []
            
            videos = []
            
            # Try different data structures for hashtag pages
            # Pattern 1: ItemModule (similar to profile)
            if 'ItemModule' in data:
                item_module = data['ItemModule']
                for video_id, video_data in item_module.items():
                    parsed = self._parse_video_data(video_data)
                    if parsed and self._filter_video(parsed, since, until):
                        videos.append(parsed)
                        if len(videos) >= limit:
                            break
            
            # Pattern 2: ChallengeModule
            elif 'ChallengeModule' in data:
                challenge_module = data['ChallengeModule']
                for challenge_id, challenge_data in challenge_module.items():
                    video_list = challenge_data.get('videoList', [])
                    for video_id in video_list[:limit]:
                        if 'ItemModule' in data and video_id in data['ItemModule']:
                            video_data = data['ItemModule'][video_id]
                            parsed = self._parse_video_data(video_data)
                            if parsed and self._filter_video(parsed, since, until):
                                videos.append(parsed)
                                if len(videos) >= limit:
                                    break
            
            # Pattern 3: webapp structure
            elif 'webapp' in data:
                webapp = data['webapp']
                
                # Try challenge-detail path
                if 'challenge-detail' in webapp:
                    challenge_detail = webapp['challenge-detail']
                    if 'challengeInfo' in challenge_detail:
                        # Videos might be in ItemList
                        pass
                
                # Try to find ItemList
                if 'ItemList' in webapp:
                    item_list = webapp['ItemList']
                    if 'challenge' in item_list:
                        challenge_items = item_list['challenge']
                        if 'list' in challenge_items:
                            for video_id in challenge_items['list'][:limit]:
                                # Need to find video data
                                pass
            
            return videos[:limit]
            
        except Exception as e:
            log.error(f"HTTP scraping error: {str(e)}")
            return []
    
    async def _scrape_with_playwright(
        self,
        hashtag: str,
        limit: int,
        since: Optional[datetime],
        until: Optional[datetime]
    ) -> List[Dict]:
        """Scrape using Playwright headless browser"""
        try:
            # Try enhanced scraper first
            from app.scrapers.enhanced_scraper import EnhancedTikTokScraper
            
            async with EnhancedTikTokScraper() as scraper:
                videos = await scraper.scrape_hashtag(hashtag, limit)
                
                # Filter by date if needed
                if videos and (since or until):
                    videos = [v for v in videos if self._filter_video(v, since, until)]
                
                return videos
                
        except Exception as e:
            log.error(f"Enhanced scraping error: {str(e)}")
            
            # Fallback to original Playwright scraper
            try:
                async with PlaywrightScraper() as scraper:
                    videos = await scraper.scrape_hashtag(hashtag, limit, since, until)
                    return videos
            except Exception as e2:
                log.error(f"Playwright scraping error: {str(e2)}")
                return []
    
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
        
        # Convert timestamp to datetime if needed
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
