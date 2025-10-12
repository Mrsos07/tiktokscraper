import httpx
import asyncio
import random
import json
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from parsel import Selector
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.core.logging import log


class BaseScraper(ABC):
    """Base class for TikTok scrapers"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.init_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
    
    async def init_session(self):
        """Initialize HTTP session with HTTP/2 support"""
        headers = self._get_headers()
        
        # Configure client parameters
        client_params = {
            'http2': False,  # Disabled temporarily due to h2 package issues
            'headers': headers,
            'timeout': settings.TIKTOK_TIMEOUT,
            'follow_redirects': True,
        }
        
        # Add proxy if configured
        if settings.USE_PROXY and settings.PROXY_URL:
            client_params['proxy'] = settings.PROXY_URL
        
        self.session = httpx.AsyncClient(**client_params)
        
        log.info("HTTP session initialized with HTTP/2 support")
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.aclose()
            log.info("HTTP session closed")
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate realistic browser headers"""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
    
    async def _random_delay(self):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(
            settings.TIKTOK_REQUEST_DELAY_MIN,
            settings.TIKTOK_REQUEST_DELAY_MAX
        )
        await asyncio.sleep(delay)
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=8, max=30)
    )
    async def _fetch_page(self, url: str) -> str:
        """Fetch page HTML with retries"""
        if not self.session:
            await self.init_session()
        
        log.info(f"Fetching URL: {url}")
        
        try:
            # Add delay before request to avoid rate limiting
            await self._random_delay()
            
            response = await self.session.get(url)
            
            # Handle rate limiting
            if response.status_code == 429:
                log.warning(f"Rate limited! Waiting 30 seconds...")
                await asyncio.sleep(30)
                raise httpx.HTTPStatusError("Rate limited", request=response.request, response=response)
            
            response.raise_for_status()
            
            return response.text
        except httpx.HTTPStatusError as e:
            log.error(f"HTTP error {e.response.status_code} for {url}")
            raise
        except Exception as e:
            log.error(f"Error fetching {url}: {str(e)}")
            raise
    
    def _extract_json_from_script(self, html: str, script_id: str = "SIGI_STATE") -> Optional[Dict]:
        """Extract JSON data from script tag"""
        try:
            selector = Selector(text=html)
            
            # Try multiple script ID patterns
            script_ids = [
                "SIGI_STATE",
                "__UNIVERSAL_DATA_FOR_REHYDRATION__",
                "SIGI_RETRY_STATE"
            ]
            
            for sid in script_ids:
                script = selector.xpath(f'//script[@id="{sid}"]/text()').get()
                if script:
                    log.info(f"Found script with ID: {sid}")
                    return json.loads(script)
            
            # Try to find any script with TikTok data
            scripts = selector.xpath('//script[contains(text(), "webapp")]/text()').getall()
            for script in scripts:
                try:
                    data = json.loads(script)
                    if isinstance(data, dict) and any(key in data for key in ['UserModule', 'ItemModule', 'webapp']):
                        log.info("Found TikTok data in script tag")
                        return data
                except json.JSONDecodeError:
                    continue
            
            log.warning("No JSON data found in script tags")
            return None
            
        except Exception as e:
            log.error(f"Error extracting JSON from script: {str(e)}")
            return None
    
    def _parse_video_data(self, video_data: Dict) -> Optional[Dict]:
        """Parse video data from TikTok JSON structure"""
        try:
            # Extract common fields
            video_id = video_data.get('id') or video_data.get('video', {}).get('id')
            
            if not video_id:
                return None
            
            # Author info
            author = video_data.get('author', {})
            author_username = author.get('uniqueId') or author.get('username')
            author_nickname = author.get('nickname')
            
            # Video metadata
            desc = video_data.get('desc') or video_data.get('description', '')
            
            # Statistics
            stats = video_data.get('stats', {})
            views = stats.get('playCount', 0) or stats.get('viewCount', 0)
            likes = stats.get('diggCount', 0) or stats.get('likeCount', 0)
            comments = stats.get('commentCount', 0)
            shares = stats.get('shareCount', 0)
            
            # Timestamps
            create_time = video_data.get('createTime') or video_data.get('createdAt')
            
            # Hashtags
            hashtags = []
            challenges = video_data.get('challenges', []) or video_data.get('textExtra', [])
            for challenge in challenges:
                if isinstance(challenge, dict):
                    tag = challenge.get('title') or challenge.get('hashtagName')
                    if tag:
                        hashtags.append(tag.lstrip('#'))
            
            # Music
            music = video_data.get('music', {})
            music_title = music.get('title')
            music_author = music.get('authorName')
            
            # Video URL - Try multiple patterns
            video_info = video_data.get('video', {})
            video_url = None
            
            # Try multiple URL patterns from video object
            if 'downloadAddr' in video_info:
                video_url = video_info['downloadAddr']
            elif 'playAddr' in video_info:
                video_url = video_info['playAddr']
            elif 'playbackUrl' in video_info:
                video_url = video_info['playbackUrl']
            
            # If video_url is a dict, extract the actual URL
            if isinstance(video_url, dict):
                video_url = video_url.get('UrlList', [None])[0] or video_url.get('url')
            
            # Try alternative locations in video_data
            if not video_url:
                video_url = video_data.get('downloadAddr') or video_data.get('playAddr')
                if isinstance(video_url, dict):
                    video_url = video_url.get('UrlList', [None])[0] or video_url.get('url')
            
            # Duration
            duration = video_info.get('duration')
            if not duration:
                duration = video_data.get('duration')
            
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
    
    @abstractmethod
    async def scrape(self, value: str, limit: int = 50, **kwargs) -> List[Dict]:
        """Abstract method to be implemented by subclasses"""
        pass
