"""
Simple Working Scraper - No Playwright, Pure HTTP
"""
import httpx
import re
import json
from typing import List, Dict
from pathlib import Path
from app.core.logging import log


async def scrape_and_download(username: str, limit: int = 1, output_dir: Path = None) -> List[Dict]:
    """
    Simple scraper that actually works
    """
    username = username.lstrip('@')
    url = f"https://www.tiktok.com/@{username}"
    
    log.info(f"🎯 Scraping @{username}")
    
    if not output_dir:
        output_dir = Path("downloads/profile") / username
    output_dir.mkdir(parents=True, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            # Get profile page
            log.info("📄 Loading profile...")
            response = await client.get(url, headers=headers)
            html = response.text
            
            # Extract video IDs - try multiple patterns
            video_ids = []
            
            # Pattern 1: From video URLs
            ids = re.findall(r'/@[^/]+/video/(\d{19})', html)
            video_ids.extend(ids)
            
            # Pattern 2: From JSON data
            ids = re.findall(r'"id":"(\d{19})"', html)
            video_ids.extend(ids)
            
            # Pattern 3: Simple video ID pattern
            ids = re.findall(r'video/(\d{19})', html)
            video_ids.extend(ids)
            
            # Remove duplicates, keep order
            seen = set()
            unique_ids = []
            for vid_id in video_ids:
                if vid_id not in seen:
                    seen.add(vid_id)
                    unique_ids.append(vid_id)
            
            video_ids = unique_ids[:limit]
            
            log.info(f"   Found {len(video_ids)} video IDs: {video_ids}")
            
            if not video_ids:
                log.warning("⚠️ No videos found in HTML")
                log.info(f"   HTML length: {len(html)} chars")
                # Save HTML for debugging
                with open("debug_profile.html", "w", encoding="utf-8") as f:
                    f.write(html)
                log.info("   Saved HTML to debug_profile.html")
                return []
            
            log.info(f"✅ Found {len(video_ids)} videos")
            
            results = []
            for i, vid_id in enumerate(video_ids, 1):
                video_url = f"https://www.tiktok.com/@{username}/video/{vid_id}"
                log.info(f"\n📹 [{i}/{len(video_ids)}] Video {vid_id}")
                
                # Get video page
                response = await client.get(video_url, headers=headers)
                html = response.text
                
                # Extract download URL
                download_url = None
                
                # Try SIGI_STATE
                match = re.search(r'<script id="SIGI_STATE"[^>]*>([^<]+)</script>', html)
                if match:
                    try:
                        data = json.loads(match.group(1))
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
                
                # Try __UNIVERSAL_DATA_FOR_REHYDRATION__
                if not download_url:
                    match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>([^<]+)</script>', html)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            scope = data.get('__DEFAULT_SCOPE__', {})
                            detail = scope.get('webapp.video-detail', {})
                            item = detail.get('itemInfo', {}).get('itemStruct', {})
                            video_info = item.get('video', {})
                            
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
                        except:
                            pass
                
                if not download_url:
                    log.warning(f"   ⚠️ No download URL found")
                    results.append({
                        'video_id': vid_id,
                        'url': video_url,
                        'success': False,
                        'file_path': None,
                        'author_username': username,
                    })
                    continue
                
                # Download video
                log.info(f"   📥 Downloading...")
                output_file = output_dir / f"{vid_id}.mp4"
                
                try:
                    response = await client.get(download_url, headers=headers)
                    response.raise_for_status()
                    
                    with open(output_file, 'wb') as f:
                        f.write(response.content)
                    
                    size_mb = len(response.content) / 1024 / 1024
                    log.info(f"   ✅ Downloaded: {size_mb:.2f} MB")
                    log.info(f"   💾 Saved: {output_file}")
                    
                    results.append({
                        'video_id': vid_id,
                        'url': video_url,
                        'success': True,
                        'file_path': str(output_file),
                        'author_username': username,
                    })
                    
                except Exception as e:
                    log.error(f"   ❌ Download failed: {e}")
                    results.append({
                        'video_id': vid_id,
                        'url': video_url,
                        'success': False,
                        'file_path': None,
                        'author_username': username,
                    })
            
            success_count = sum(1 for r in results if r['success'])
            log.info(f"\n✅ Completed: {success_count}/{len(results)} videos downloaded")
            
            return results
            
    except Exception as e:
        log.error(f"❌ Error: {e}")
        import traceback
        log.error(traceback.format_exc())
        return []
