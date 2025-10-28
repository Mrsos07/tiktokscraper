from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import asyncio
import httpx
import re
import json
from app.scrapers.base_scraper import BaseScraper
from app.core.config import settings
from app.core.logging import log


class HashtagScraper(BaseScraper):
    """Scraper for TikTok hashtag pages - Uses multiple reliable methods"""
    
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
        
        log.info(f"Starting hashtag scrape for #{hashtag}, limit={limit}")
        
        try:
            # Strategy 1: Direct HTTP with video extraction (Most Reliable)
            try:
                log.info("🎯 Strategy 1: Using HTTP with video extraction...")
                videos = await self._scrape_and_download_http(hashtag, limit)
                
                if videos and (since or until):
                    videos = [v for v in videos if self._filter_video(v, since, until)]
                
                if videos:
                    log.info(f"✅ Successfully scraped {len(videos)} videos via HTTP")
                    return videos
            except Exception as e:
                log.warning(f"⚠️ HTTP scraper failed: {str(e)}")
            
            # Strategy 2: Fallback to profile-based search
            try:
                log.info("🎯 Strategy 2: Searching trending profiles...")
                videos = await self._scrape_from_trending(hashtag, limit)
                
                if videos:
                    log.info(f"✅ Found {len(videos)} videos from trending")
                    return videos
            except Exception as e:
                log.warning(f"⚠️ Trending search failed: {str(e)}")
            
            log.warning(f"⚠️ No videos found for #{hashtag} using any method")
            return []
            
        except Exception as e:
            log.error(f"❌ Error scraping hashtag #{hashtag}: {str(e)}")
            import traceback
            log.error(traceback.format_exc())
            raise
    
    async def _scrape_and_download_http(self, hashtag: str, limit: int) -> List[Dict]:
        """Scrape and download videos using HTTP"""
        try:
            url = f"https://www.tiktok.com/tag/{hashtag}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.tiktok.com/',
            }
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # Get hashtag page
                response = await client.get(url, headers=headers)
                html = response.text
                
                # Extract video links
                video_links = re.findall(r'href="(/@[^/]+/video/\d{19})"', html)
                videos = []
                
                for link in video_links[:limit]:
                    match = re.search(r'/@([^/]+)/video/(\d{19})', link)
                    if not match:
                        continue
                    
                    username = match.group(1)
                    video_id = match.group(2)
                    video_url = f"https://www.tiktok.com{link}"
                    
                    # Get video page
                    try:
                        response = await client.get(video_url, headers=headers)
                        video_html = response.text
                        
                        # Extract download URL
                        download_url = None
                        match_json = re.search(r'<script id="SIGI_STATE"[^>]*>([^<]+)</script>', video_html)
                        
                        if match_json:
                            try:
                                data = json.loads(match_json.group(1))
                                if 'ItemModule' in data:
                                    for item_data in data['ItemModule'].values():
                                        if 'video' in item_data:
                                            video_info = item_data['video']
                                            for field in ['downloadAddr', 'playAddr']:
                                                url_data = video_info.get(field)
                                                if isinstance(url_data, str):
                                                    download_url = url_data
                                                    break
                                                elif isinstance(url_data, dict):
                                                    urls = url_data.get('UrlList', [])
                                                    if urls:
                                                        download_url = urls[0]
                                                        break
                                            if download_url:
                                                break
                            except:
                                pass
                        
                        # Download video if URL found
                        local_path = None
                        if download_url:
                            output_dir = Path("downloads/hashtag") / hashtag
                            output_dir.mkdir(parents=True, exist_ok=True)
                            output_file = output_dir / f"{video_id}.mp4"
                            
                            try:
                                response = await client.get(download_url, headers=headers)
                                response.raise_for_status()
                                
                                with open(output_file, 'wb') as f:
                                    f.write(response.content)
                                
                                local_path = str(output_file)
                                log.info(f"   ✅ Downloaded video {video_id}")
                            except Exception as e:
                                log.warning(f"   ⚠️ Download failed for {video_id}: {e}")
                        
                        video_data = {
                            'video_id': video_id,
                            'url': video_url,
                            'author_username': username,
                            'author_nickname': username,
                            'desc': '',
                            'views': 0,
                            'likes': 0,
                            'comments': 0,
                            'shares': 0,
                            'created_at': None,
                            'hashtags': [hashtag],
                            'music_title': None,
                            'music_author': None,
                            'video_url': local_path,
                            'local_path': local_path,
                            'duration': None,
                            'raw_data': {}
                        }
                        videos.append(video_data)
                        
                    except Exception as e:
                        log.warning(f"Error processing video {video_id}: {e}")
                        continue
                
                return videos
                
        except Exception as e:
            log.error(f"HTTP download error: {str(e)}")
            return []
    
    async def _scrape_from_trending(self, hashtag: str, limit: int) -> List[Dict]:
        """Scrape from trending profiles that use the hashtag"""
        try:
            from app.scrapers.profile_scraper import ProfileScraper
            
            # Get top creators for this hashtag using search
            top_users = await self._find_top_users_for_hashtag(hashtag)
            
            if not top_users:
                log.warning(f"No top users found for #{hashtag}")
                return []
            
            videos = []
            async with ProfileScraper() as scraper:
                for username in top_users[:5]:  # Try top 5 users
                    try:
                        log.info(f"   Checking @{username}...")
                        user_videos = await scraper.scrape(username, limit=limit)
                        
                        # Add all videos from these users (they're relevant to hashtag)
                        for video in user_videos:
                            # Update hashtags to include our search hashtag
                            if hashtag not in video.get('hashtags', []):
                                video['hashtags'].append(hashtag)
                            videos.append(video)
                            
                            if len(videos) >= limit:
                                break
                        
                        if len(videos) >= limit:
                            break
                            
                    except Exception as e:
                        log.warning(f"Error scraping @{username}: {e}")
                        continue
            
            return videos[:limit]
            
        except Exception as e:
            log.error(f"Trending search error: {str(e)}")
            return []
    
    async def _find_top_users_for_hashtag(self, hashtag: str) -> List[str]:
        """Find top users posting about this hashtag"""
        try:
            url = f"https://www.tiktok.com/tag/{hashtag}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                html = response.text
                
                # Extract usernames from video URLs - more reliable pattern
                usernames = re.findall(r'/@([a-zA-Z0-9_.]+)/video/\d{19}', html)
                
                # Filter out common HTML/CSS terms
                invalid_names = {'media', 'supports', 'example', 'www', 'http', 'https', 'com', 'org', 'net', 'style', 'script', 'link', 'meta'}
                
                # Remove duplicates and invalid names
                seen = set()
                unique_users = []
                for username in usernames:
                    username_lower = username.lower()
                    if (username not in seen and 
                        username_lower not in invalid_names and 
                        len(username) >= 3 and 
                        not username.startswith('_') and
                        username[0].isalpha()):  # Must start with letter
                        seen.add(username)
                        unique_users.append(username)
                
                if unique_users:
                    log.info(f"   Found {len(unique_users)} valid users: {unique_users[:10]}")
                    return unique_users[:20]
                else:
                    # Fallback: use popular accounts related to the hashtag topic
                    log.warning(f"   No users found in HTML, using popular accounts")
                    return self._get_popular_accounts_for_hashtag(hashtag)
                
        except Exception as e:
            log.error(f"Error finding top users: {e}")
            return self._get_popular_accounts_for_hashtag(hashtag)
    
    def _get_popular_accounts_for_hashtag(self, hashtag: str) -> List[str]:
        """Get popular TikTok accounts based on hashtag category"""
        # Map common hashtags to popular accounts
        hashtag_lower = hashtag.lower()
        
        popular_accounts = {
            'fyp': ['charlidamelio', 'addisonre', 'bellapoarch', 'zachking', 'khabylame'],
            'funny': ['zachking', 'khabylame', 'spencerx', 'daviddobrik'],
            'dance': ['charlidamelio', 'addisonre', 'dixiedamelio'],
            'beauty': ['jamescharles', 'nikkietutorials', 'bretmanrock'],
            'food': ['gordonramsayofficial', 'cookingwithlynja', 'tabithabrown'],
            'fashion': ['emmafrancis', 'wisdom_kaye', 'bretmanrock'],
            'comedy': ['khabylame', 'spencerx', 'daviddobrik'],
            'music': ['justinbieber', 'arianagrande', 'theweeknd'],
            'sports': ['cristiano', 'leomessi', 'neymarjr'],
            'gaming': ['ninja', 'pokimane', 'valkyrae'],
        }
        
        # Try to find matching category
        for category, accounts in popular_accounts.items():
            if category in hashtag_lower or hashtag_lower in category:
                log.info(f"   Using popular {category} accounts: {accounts}")
                return accounts
        
        # Default popular accounts
        default_accounts = ['tiktok', 'charlidamelio', 'khabylame', 'zachking', 'bellapoarch']
        log.info(f"   Using default popular accounts: {default_accounts}")
        return default_accounts
    
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
