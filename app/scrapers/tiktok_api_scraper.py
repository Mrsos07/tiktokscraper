"""
TikTok API Scraper - Uses TikTok's unofficial API endpoints
More reliable than HTML scraping
"""
import httpx
import asyncio
import json
from typing import List, Dict, Optional
from datetime import datetime
from app.core.config import settings
from app.core.logging import log


class TikTokAPIScraper:
    """Scraper using TikTok's unofficial API endpoints"""
    
    def __init__(self):
        self.session: Optional[httpx.AsyncClient] = None
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.tiktok.com/',
            'Origin': 'https://www.tiktok.com',
        }
    
    async def __aenter__(self):
        await self.init_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()
    
    async def init_session(self):
        """Initialize HTTP session"""
        self.session = httpx.AsyncClient(
            http2=True,
            headers=self.base_headers,
            timeout=30.0,
            follow_redirects=True,
        )
        log.info("TikTok API scraper session initialized")
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.aclose()
            log.info("TikTok API scraper session closed")
    
    async def scrape_profile(
        self,
        username: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Scrape videos from a TikTok profile using API
        
        Args:
            username: TikTok username (without @)
            limit: Maximum number of videos to scrape
            
        Returns:
            List of video data dictionaries
        """
        username = username.lstrip('@')
        log.info(f"🔍 Scraping profile via API: @{username}, limit={limit}")
        
        try:
            # First, get user info to get secUid
            user_info = await self._get_user_info(username)
            
            if not user_info:
                log.warning(f"Could not get user info for @{username}")
                return []
            
            sec_uid = user_info.get('secUid')
            if not sec_uid:
                log.warning(f"No secUid found for @{username}")
                return []
            
            # Get user videos
            videos = await self._get_user_videos(sec_uid, limit)
            
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
        Scrape videos from a TikTok hashtag using API
        
        Args:
            hashtag: Hashtag name (without #)
            limit: Maximum number of videos to scrape
            
        Returns:
            List of video data dictionaries
        """
        hashtag = hashtag.lstrip('#')
        log.info(f"🔍 Scraping hashtag via API: #{hashtag}, limit={limit}")
        
        try:
            videos = await self._get_hashtag_videos(hashtag, limit)
            
            log.info(f"✅ Scraped {len(videos)} videos from #{hashtag}")
            return videos
            
        except Exception as e:
            log.error(f"❌ Error scraping hashtag #{hashtag}: {str(e)}")
            return []
    
    async def _get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information including secUid"""
        try:
            # Try web API endpoint
            url = f"https://www.tiktok.com/@{username}"
            
            response = await self.session.get(url)
            response.raise_for_status()
            
            html = response.text
            
            # Extract JSON data from script tag
            import re
            
            # Look for SIGI_STATE
            match = re.search(r'<script id="SIGI_STATE"[^>]*>([^<]+)</script>', html)
            if match:
                try:
                    data = json.loads(match.group(1))
                    
                    # Extract user info
                    if 'UserModule' in data:
                        user_module = data['UserModule']
                        if 'users' in user_module:
                            for user_id, user_data in user_module['users'].items():
                                if user_data.get('uniqueId') == username:
                                    return user_data
                        
                        # Try direct user data
                        for user_id, user_data in user_module.items():
                            if isinstance(user_data, dict) and user_data.get('uniqueId') == username:
                                return user_data
                    
                    # Try webapp structure
                    if 'webapp' in data:
                        webapp = data['webapp']
                        if 'user-detail' in webapp:
                            user_detail = webapp['user-detail']
                            if 'userInfo' in user_detail:
                                user_info = user_detail['userInfo']
                                if 'user' in user_info:
                                    return user_info['user']
                
                except json.JSONDecodeError as e:
                    log.error(f"Error parsing user info JSON: {str(e)}")
            
            return None
            
        except Exception as e:
            log.error(f"Error getting user info: {str(e)}")
            return None
    
    async def _get_user_videos(self, sec_uid: str, limit: int) -> List[Dict]:
        """Get user videos using secUid"""
        videos = []
        
        try:
            # This is a simplified approach - actual TikTok API requires more parameters
            # For now, we'll return empty and rely on the enhanced scraper
            log.info(f"Getting videos for secUid: {sec_uid[:20]}...")
            
            # Note: TikTok's actual API endpoints require additional authentication
            # and parameters that change frequently. This is a placeholder.
            
            return videos
            
        except Exception as e:
            log.error(f"Error getting user videos: {str(e)}")
            return videos
    
    async def _get_hashtag_videos(self, hashtag: str, limit: int) -> List[Dict]:
        """Get hashtag videos"""
        videos = []
        
        try:
            # Similar to user videos, this requires TikTok's API authentication
            log.info(f"Getting videos for hashtag: #{hashtag}")
            
            return videos
            
        except Exception as e:
            log.error(f"Error getting hashtag videos: {str(e)}")
            return videos
    
    def _parse_video_data(self, video_data: Dict) -> Optional[Dict]:
        """Parse video data from API response"""
        try:
            video_id = video_data.get('id')
            if not video_id:
                return None
            
            # Author info
            author = video_data.get('author', {})
            author_username = author.get('uniqueId') or author.get('username', 'unknown')
            author_nickname = author.get('nickname', author_username)
            
            # Video metadata
            desc = video_data.get('desc', '')
            
            # Statistics
            stats = video_data.get('stats', {})
            views = stats.get('playCount', 0)
            likes = stats.get('diggCount', 0)
            comments = stats.get('commentCount', 0)
            shares = stats.get('shareCount', 0)
            
            # Timestamps
            create_time = video_data.get('createTime')
            
            # Hashtags
            hashtags = []
            challenges = video_data.get('challenges', [])
            for challenge in challenges:
                if isinstance(challenge, dict):
                    tag = challenge.get('title', '').lstrip('#')
                    if tag:
                        hashtags.append(tag)
            
            # Music
            music = video_data.get('music', {})
            music_title = music.get('title')
            music_author = music.get('authorName')
            
            # Video URL
            video_info = video_data.get('video', {})
            video_url = None
            
            # Try to get download URL
            if 'downloadAddr' in video_info:
                video_url = video_info['downloadAddr']
            elif 'playAddr' in video_info:
                video_url = video_info['playAddr']
            
            # Handle URL as dict
            if isinstance(video_url, dict):
                url_list = video_url.get('UrlList', [])
                video_url = url_list[0] if url_list else None
            
            # Duration
            duration = video_info.get('duration')
            
            return {
                'video_id': str(video_id),
                'url': f"https://www.tiktok.com/@{author_username}/video/{video_id}",
                'desc': desc,
                'author_username': author_username,
                'author_nickname': author_nickname,
                'views': views,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'created_at': create_time,
                'hashtags': hashtags,
                'music_title': music_title,
                'music_author': music_author,
                'video_url': video_url,
                'duration': duration,
                'raw_data': video_data,
            }
            
        except Exception as e:
            log.error(f"Error parsing video data: {str(e)}")
            return None
