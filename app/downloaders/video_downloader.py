import httpx
import asyncio
from pathlib import Path
from typing import Optional, Dict
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.core.logging import log


class VideoDownloader:
    """Download TikTok videos with no-watermark support"""
    
    def __init__(self):
        self.session: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.init_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
    
    async def init_session(self):
        """Initialize HTTP session"""
        self.session = httpx.AsyncClient(
            http2=True,
            timeout=60.0,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        log.info("Video downloader session initialized")
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.aclose()
            log.info("Video downloader session closed")
    
    async def download_video(
        self,
        video_data: Dict,
        output_path: Path,
        no_watermark: bool = True
    ) -> Dict:
        """
        Download video with optional no-watermark
        
        Args:
            video_data: Video metadata dictionary
            output_path: Path to save video file
            no_watermark: Attempt to download without watermark
            
        Returns:
            Dictionary with download info (success, file_size, has_watermark, etc.)
        """
        video_id = video_data['video_id']
        log.info(f"Downloading video {video_id}, no_watermark={no_watermark}")
        
        try:
            # Strategy 1: Try direct video URL from scraped data
            video_url = video_data.get('video_url')
            
            log.info(f"Video URL from scraper: {video_url[:100] if video_url else 'None'}")
            
            if video_url and isinstance(video_url, str) and video_url.startswith('http'):
                log.info(f"✅ Valid video URL found, attempting download...")
                result = await self._download_from_url(video_url, output_path)
                if result['success']:
                    result['has_watermark'] = False  # downloadAddr is without watermark
                    log.info(f"✅ Downloaded {video_id} successfully ({result['file_size']} bytes)")
                    return result
                else:
                    log.warning(f"⚠️ Failed to download from scraped URL: {result.get('error')}")
            else:
                log.warning(f"❌ No valid video URL in scraped data")
            
            # Strategy 2: Try no-watermark extraction methods
            if no_watermark:
                # Method 2a: Try to extract from TikTok CDN patterns
                result = await self._download_nowatermark_cdn(video_data, output_path)
                if result['success']:
                    log.info(f"Downloaded {video_id} without watermark (CDN)")
                    return result
                
                # Method 2b: Try external API if configured
                if settings.NOWATERMARK_API_KEY and settings.NOWATERMARK_API_URL:
                    result = await self._download_via_external_api(video_data, output_path)
                    if result['success']:
                        log.info(f"Downloaded {video_id} without watermark (External API)")
                        return result
            
            # Strategy 3: Fallback to extracting URL from TikTok page
            log.info(f"Attempting to extract video URL from page: {video_data['url']}")
            video_url = await self._extract_video_url(video_data['url'])
            if video_url:
                log.info(f"✅ Extracted video URL from page: {video_url[:100]}")
                result = await self._download_from_url(video_url, output_path)
                if result['success']:
                    result['has_watermark'] = True
                    log.info(f"✅ Downloaded {video_id} with watermark (fallback)")
                    return result
            else:
                log.error(f"❌ Could not extract video URL from page")
            
            log.error(f"❌ All download strategies failed for video {video_id}")
            return {
                'success': False,
                'error': 'No valid download URL found - all strategies failed',
                'has_watermark': None,
                'file_size': 0
            }
            
        except Exception as e:
            log.error(f"Error downloading video {video_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'has_watermark': None,
                'file_size': 0
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _download_from_url(self, url: str, output_path: Path) -> Dict:
        """Download video from direct URL"""
        try:
            if not self.session:
                await self.init_session()
            
            # Validate URL
            if not url or not isinstance(url, str) or not url.startswith('http'):
                return {
                    'success': False,
                    'error': f'Invalid URL: {url}',
                    'file_size': 0
                }
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Stream download
            async with self.session.stream('GET', url) as response:
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if 'video' not in content_type and 'octet-stream' not in content_type:
                    log.warning(f"Unexpected content type: {content_type}")
                
                file_size = 0
                with open(output_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        file_size += len(chunk)
                
                # Verify file was written
                if file_size == 0 or not output_path.exists():
                    return {
                        'success': False,
                        'error': 'Downloaded file is empty or not saved',
                        'file_size': 0
                    }
                
                log.info(f"Downloaded {file_size} bytes to {output_path}")
                
                return {
                    'success': True,
                    'file_size': file_size,
                    'local_path': str(output_path)
                }
                
        except httpx.HTTPStatusError as e:
            log.error(f"HTTP error {e.response.status_code} downloading from {url}")
            return {
                'success': False,
                'error': f'HTTP {e.response.status_code}: {str(e)}',
                'file_size': 0
            }
        except Exception as e:
            log.error(f"Error downloading from URL {url}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_size': 0
            }
    
    async def _download_nowatermark_cdn(self, video_data: Dict, output_path: Path) -> Dict:
        """
        Attempt to download no-watermark version using CDN URL patterns
        
        TikTok sometimes exposes no-watermark URLs through specific CDN patterns.
        This is a heuristic approach that may break when TikTok changes their system.
        """
        try:
            video_url = video_data.get('video_url')
            if not video_url:
                return {'success': False, 'error': 'No video URL'}
            
            # Try to modify URL to get no-watermark version
            # Pattern 1: Replace 'watermark=1' with 'watermark=0'
            nowm_url = video_url.replace('watermark=1', 'watermark=0')
            
            if nowm_url != video_url:
                result = await self._download_from_url(nowm_url, output_path)
                if result['success']:
                    result['has_watermark'] = False
                    return result
            
            # Pattern 2: Try 'wm' parameter
            if '?' in video_url:
                nowm_url = video_url + '&wm=0'
            else:
                nowm_url = video_url + '?wm=0'
            
            result = await self._download_from_url(nowm_url, output_path)
            if result['success']:
                result['has_watermark'] = False
                return result
            
            return {'success': False, 'error': 'No-watermark CDN patterns failed'}
            
        except Exception as e:
            log.error(f"Error in no-watermark CDN download: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _download_via_external_api(self, video_data: Dict, output_path: Path) -> Dict:
        """
        Download using external no-watermark API service
        
        This requires an external API key configured in settings.
        Example services: SnapTik API, TikMate API, etc.
        """
        try:
            if not self.session:
                await self.init_session()
            
            # Example API call structure (adjust based on actual API)
            api_url = settings.NOWATERMARK_API_URL
            headers = {
                'Authorization': f'Bearer {settings.NOWATERMARK_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'url': video_data['url'],
                'no_watermark': True
            }
            
            response = await self.session.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract download URL from API response (structure varies by API)
            download_url = data.get('download_url') or data.get('video_url')
            
            if not download_url:
                return {'success': False, 'error': 'No download URL from API'}
            
            # Download from the provided URL
            result = await self._download_from_url(download_url, output_path)
            if result['success']:
                result['has_watermark'] = False
                return result
            
            return {'success': False, 'error': 'Failed to download from API URL'}
            
        except Exception as e:
            log.error(f"Error downloading via external API: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _extract_video_url(self, tiktok_url: str) -> Optional[str]:
        """
        Extract video download URL from TikTok page
        Fallback method when direct URL is not available
        """
        try:
            if not self.session:
                await self.init_session()
            
            log.info(f"Extracting video URL from page: {tiktok_url}")
            
            response = await self.session.get(tiktok_url)
            response.raise_for_status()
            
            html = response.text
            
            # Try to parse JSON from script tags first
            import re
            import json
            
            # Look for SIGI_STATE or similar script tags
            script_patterns = [
                r'<script id="SIGI_STATE"[^>]*>([^<]+)</script>',
                r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>([^<]+)</script>',
            ]
            
            for script_pattern in script_patterns:
                script_match = re.search(script_pattern, html)
                if script_match:
                    try:
                        data = json.loads(script_match.group(1))
                        
                        # Try to find video URL in the data structure
                        if 'ItemModule' in data:
                            for item_id, item_data in data['ItemModule'].items():
                                video_info = item_data.get('video', {})
                                
                                # Try different URL fields
                                for url_field in ['downloadAddr', 'playAddr', 'playbackUrl']:
                                    url_data = video_info.get(url_field)
                                    if url_data:
                                        if isinstance(url_data, str):
                                            return url_data
                                        elif isinstance(url_data, dict):
                                            url_list = url_data.get('UrlList', [])
                                            if url_list:
                                                return url_list[0]
                    except json.JSONDecodeError:
                        continue
            
            # Fallback: Try regex patterns for video URLs
            patterns = [
                r'"downloadAddr":"([^"]+)"',
                r'"playAddr":"([^"]+)"',
                r'"playbackUrl":"([^"]+)"',
                r'"UrlList":\["([^"]+)"',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    url = match.group(1)
                    # Unescape URL
                    url = url.encode().decode('unicode_escape')
                    if url.startswith('http'):
                        log.info(f"Extracted video URL using pattern: {pattern}")
                        return url
            
            log.warning("No video URL found in page")
            return None
            
        except Exception as e:
            log.error(f"Error extracting video URL: {str(e)}")
            return None
    
    async def get_video_info(self, url: str) -> Optional[Dict]:
        """Get video file information without downloading"""
        try:
            if not self.session:
                await self.init_session()
            
            response = await self.session.head(url)
            response.raise_for_status()
            
            return {
                'content_type': response.headers.get('content-type'),
                'content_length': int(response.headers.get('content-length', 0)),
                'url': str(response.url)
            }
            
        except Exception as e:
            log.error(f"Error getting video info: {str(e)}")
            return None
