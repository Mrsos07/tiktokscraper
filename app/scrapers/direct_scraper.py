"""
Direct TikTok scraper - simple and effective
"""
import httpx
import json
import re
from typing import List, Dict, Optional
from app.core.logging import log


async def scrape_profile_simple(username: str, limit: int = 10) -> List[Dict]:
    """Simple direct scraping"""
    username = username.lstrip('@')
    url = f"https://www.tiktok.com/@{username}"
    
    log.info(f"Direct scraping: @{username}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.tiktok.com/',
    }
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            html = response.text
            
            # Extract video IDs from HTML - get the most recent ones
            # Look for video IDs in various patterns
            patterns = [
                r'/@[^/]+/video/(\d{19})',  # From video URLs
                r'"id":"(\d{19})"',  # From JSON
                r'video/(\d{19})',  # Simple pattern
            ]
            
            video_ids = []
            for pattern in patterns:
                matches = re.findall(pattern, html)
                video_ids.extend(matches)
            
            # Remove duplicates while preserving order (most recent first)
            seen = set()
            unique_ids = []
            for vid_id in video_ids:
                if vid_id not in seen and len(vid_id) == 19:
                    seen.add(vid_id)
                    unique_ids.append(vid_id)
            
            video_ids = unique_ids[:limit]
            
            if not video_ids:
                log.warning("No video IDs found in HTML")
                return []
            
            log.info(f"Found {len(video_ids)} video IDs")
            
            videos = []
            for i, vid_id in enumerate(video_ids, 1):
                video_url = f"https://www.tiktok.com/@{username}/video/{vid_id}"
                
                log.info(f"  [{i}/{len(video_ids)}] Processing video {vid_id}")
                
                # Try to extract download URL
                download_url = await _get_download_url(client, video_url, headers)
                
                if download_url:
                    log.info(f"      ✅ Download URL found: {download_url[:80]}...")
                else:
                    log.warning(f"      ⚠️ No download URL found for video {vid_id}")
                
                video_data = {
                    'video_id': vid_id,
                    'url': video_url,
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
                    'video_url': download_url,
                    'duration': None,
                    'raw_data': {}
                }
                
                videos.append(video_data)
            
            return videos
            
    except Exception as e:
        log.error(f"Error in direct scraping: {str(e)}")
        return []


async def _get_download_url(client: httpx.AsyncClient, video_url: str, headers: dict) -> Optional[str]:
    """Extract download URL from video page"""
    try:
        response = await client.get(video_url, headers=headers)
        html = response.text
        
        # Extract from SIGI_STATE or __UNIVERSAL_DATA_FOR_REHYDRATION__
        import json
        
        # Try SIGI_STATE
        match = re.search(r'<script id="SIGI_STATE"[^>]*>([^<]+)</script>', html)
        if match:
            try:
                data = json.loads(match.group(1))
                
                # Look in ItemModule
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
            except:
                pass
        
        # Try __UNIVERSAL_DATA_FOR_REHYDRATION__
        match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>([^<]+)</script>', html)
        if match:
            try:
                data = json.loads(match.group(1))
                
                if '__DEFAULT_SCOPE__' in data:
                    default_scope = data['__DEFAULT_SCOPE__']
                    
                    if 'webapp.video-detail' in default_scope:
                        video_detail = default_scope['webapp.video-detail']
                        if 'itemInfo' in video_detail and 'itemStruct' in video_detail['itemInfo']:
                            item_struct = video_detail['itemInfo']['itemStruct']
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
            except:
                pass
        
        # Fallback: Try regex patterns
        patterns = [
            r'"downloadAddr":"([^"]+)"',
            r'"playAddr":"([^"]+)"',
            r'"UrlList":\["([^"]+)"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            if matches:
                url = matches[0]
                url = url.encode().decode('unicode_escape')
                if url.startswith('http'):
                    return url
        
        return None
        
    except Exception as e:
        log.error(f"Error getting download URL: {str(e)}")
        return None
