from typing import List, Dict, Optional
from datetime import datetime
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.playwright_scraper import PlaywrightScraper
from app.core.config import settings
from app.core.logging import log


class ProfileScraper(BaseScraper):
    """Scraper for TikTok user profiles"""
    
    async def scrape(
        self,
        username: str,
        limit: int = 50,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Scrape videos from a TikTok user profile
        
        Args:
            username: TikTok username (without @)
            limit: Maximum number of videos to scrape
            since: Filter videos created after this date
            until: Filter videos created before this date
            
        Returns:
            List of video data dictionaries
        """
        username = username.lstrip('@')
        url = f"https://www.tiktok.com/@{username}"
        
        log.info(f"Starting profile scrape for @{username}, limit={limit}")
        
        try:
            # Strategy 1: YT-DLP (Most Reliable)
            try:
                from app.scrapers.ytdlp_scraper import scrape_and_download
                from pathlib import Path
                
                log.info("🎯 Using yt-dlp (Most Reliable)...")
                
                output_dir = Path("downloads/profile") / username
                results = await scrape_and_download(username, limit, output_dir)
                
                if results:
                    # Convert to expected format
                    videos = []
                    for result in results:
                        if result['success']:
                            video_data = {
                                'video_id': result['video_id'],
                                'url': result['url'],
                                'desc': '',
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
                                'video_url': result['file_path'],  # Local file path
                                'duration': None,
                                'raw_data': {}
                            }
                            videos.append(video_data)
                    
                    if videos:
                        log.info(f"✅ Successfully downloaded {len(videos)} videos")
                        return videos
            except Exception as e:
                log.warning(f"⚠️ Simple scraper failed: {str(e)}")
                import traceback
                log.error(traceback.format_exc())
            
            # Strategy 2: HTTP request with JSON extraction
            log.info("🔍 Trying HTTP scraping...")
            videos = await self._scrape_with_http(url, limit, since, until)
            
            if videos:
                log.info(f"✅ Successfully scraped {len(videos)} videos via HTTP")
                return videos
            
            # Strategy 3: Playwright headless browser
            if settings.TIKTOK_USE_PLAYWRIGHT_FALLBACK:
                log.info("Trying Playwright fallback...")
                videos = await self._scrape_with_playwright(username, limit, since, until)
                
                if videos:
                    log.info(f"✅ Successfully scraped {len(videos)} videos via Playwright")
                    return videos
            
            log.warning(f"⚠️ No videos found for @{username} using any method")
            return []
            
        except Exception as e:
            log.error(f"❌ Error scraping profile @{username}: {str(e)}")
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
            
            # Try different data structures
            # Pattern 1: SIGI_STATE structure with ItemModule
            if 'ItemModule' in data:
                item_module = data['ItemModule']
                log.info(f"Found ItemModule with {len(item_module)} items")
                
                for video_id, video_data in item_module.items():
                    if not isinstance(video_data, dict):
                        continue
                    
                    parsed = self._parse_video_data(video_data)
                    if parsed and self._filter_video(parsed, since, until):
                        videos.append(parsed)
                        log.info(f"Parsed video: {video_id}")
                        if len(videos) >= limit:
                            break
            
            # Pattern 2: UserModule with video list
            if not videos and 'UserModule' in data:
                user_module = data['UserModule']
                log.info(f"Trying UserModule with {len(user_module)} users")
                
                for user_id, user_data in user_module.items():
                    if not isinstance(user_data, dict):
                        continue
                    
                    # Check for video list
                    video_list = user_data.get('videoList', [])
                    if video_list:
                        log.info(f"Found {len(video_list)} videos in videoList")
                        
                        for vid_id in video_list[:limit]:
                            # Try to find video data in ItemModule
                            if 'ItemModule' in data and vid_id in data['ItemModule']:
                                video_data = data['ItemModule'][vid_id]
                                parsed = self._parse_video_data(video_data)
                                if parsed and self._filter_video(parsed, since, until):
                                    videos.append(parsed)
                                    if len(videos) >= limit:
                                        break
            
            # Pattern 3: webapp structure (newer format)
            if not videos and 'webapp' in data:
                webapp = data['webapp']
                log.info("Trying webapp structure")
                
                # Try user-detail path
                if 'user-detail' in webapp:
                    user_detail = webapp['user-detail']
                    if 'userInfo' in user_detail:
                        user_info = user_detail['userInfo']
                        
                        # Check for itemList
                        if 'itemList' in user_info:
                            item_list = user_info['itemList']
                            log.info(f"Found {len(item_list)} items in itemList")
                            
                            for video_data in item_list[:limit]:
                                parsed = self._parse_video_data(video_data)
                                if parsed and self._filter_video(parsed, since, until):
                                    videos.append(parsed)
                                    if len(videos) >= limit:
                                        break
            
            if videos:
                log.info(f"Successfully extracted {len(videos)} videos via HTTP")
            else:
                log.warning("No videos extracted from any pattern")
            
            return videos[:limit]
            
        except Exception as e:
            log.error(f"HTTP scraping error: {str(e)}")
            import traceback
            log.error(traceback.format_exc())
            return []
    
    async def _scrape_with_playwright(
        self,
        username: str,
        limit: int,
        since: Optional[datetime],
        until: Optional[datetime]
    ) -> List[Dict]:
        """Scrape using Playwright headless browser"""
        try:
            # Try enhanced scraper first
            from app.scrapers.enhanced_scraper import EnhancedTikTokScraper
            
            async with EnhancedTikTokScraper() as scraper:
                videos = await scraper.scrape_profile(username, limit)
                
                # Filter by date if needed
                if videos and (since or until):
                    videos = [v for v in videos if self._filter_video(v, since, until)]
                
                return videos
                
        except Exception as e:
            log.error(f"Enhanced scraping error: {str(e)}")
            
            # Fallback to original Playwright scraper
            try:
                async with PlaywrightScraper() as scraper:
                    videos = await scraper.scrape_profile(username, limit, since, until)
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
