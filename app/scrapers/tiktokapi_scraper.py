"""
TikTok API Scraper - For hashtags
"""
from pathlib import Path
from typing import List, Dict
from TikTokApi import TikTokApi
from app.core.logging import log
import asyncio


async def scrape_hashtag_videos(hashtag: str, limit: int = 5) -> List[Dict]:
    """
    Scrape videos from hashtag using TikTokApi
    """
    hashtag = hashtag.lstrip('#')
    log.info(f"🎯 Using TikTokApi for #{hashtag}")
    
    try:
        async with TikTokApi() as api:
            tag = api.hashtag(name=hashtag)
            
            videos = []
            video_count = 0
            
            async for video in tag.videos(count=limit):
                if video_count >= limit:
                    break
                
                try:
                    video_data = {
                        'video_id': video.id,
                        'url': f"https://www.tiktok.com/@{video.author.username}/video/{video.id}",
                        'desc': video.desc or '',
                        'author_username': video.author.username,
                        'author_nickname': video.author.nickname,
                        'views': video.stats.get('playCount', 0),
                        'likes': video.stats.get('diggCount', 0),
                        'comments': video.stats.get('commentCount', 0),
                        'shares': video.stats.get('shareCount', 0),
                        'created_at': video.create_time,
                        'hashtags': [hashtag],
                        'music_title': video.music.title if video.music else None,
                        'music_author': video.music.author if video.music else None,
                        'video_url': video.video.download_addr,
                        'duration': video.video.duration,
                        'raw_data': {}
                    }
                    
                    videos.append(video_data)
                    video_count += 1
                    log.info(f"   ✅ Found video: {video.id}")
                    
                except Exception as e:
                    log.warning(f"   ⚠️ Error processing video: {e}")
                    continue
            
            log.info(f"✅ Found {len(videos)} videos for #{hashtag}")
            return videos
            
    except Exception as e:
        log.error(f"❌ TikTokApi error: {e}")
        return []
