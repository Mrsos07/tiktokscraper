"""
Simple and Reliable TikTok Scraper
Uses yt-dlp which is more reliable for TikTok scraping
"""
import asyncio
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from app.core.config import settings
from app.core.logging import log


class SimpleTikTokScraper:
    """Simple scraper using yt-dlp for reliability"""
    
    async def scrape_profile(
        self,
        username: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Scrape videos from a TikTok profile
        
        Args:
            username: TikTok username (without @)
            limit: Maximum number of videos to scrape
            
        Returns:
            List of video data dictionaries
        """
        username = username.lstrip('@')
        url = f"https://www.tiktok.com/@{username}"
        
        log.info(f"🔍 Scraping profile: @{username} (limit: {limit})")
        
        try:
            # Use yt-dlp to get video info
            videos = await self._scrape_with_ytdlp(url, limit)
            
            if videos:
                log.info(f"✅ Scraped {len(videos)} videos from @{username}")
            else:
                log.warning(f"⚠️ No videos found for @{username}")
            
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
        Scrape videos from a TikTok hashtag
        
        Args:
            hashtag: Hashtag name (without #)
            limit: Maximum number of videos to scrape
            
        Returns:
            List of video data dictionaries
        """
        hashtag = hashtag.lstrip('#')
        url = f"https://www.tiktok.com/tag/{hashtag}"
        
        log.info(f"🔍 Scraping hashtag: #{hashtag} (limit: {limit})")
        
        try:
            # Use yt-dlp to get video info
            videos = await self._scrape_with_ytdlp(url, limit)
            
            if videos:
                log.info(f"✅ Scraped {len(videos)} videos from #{hashtag}")
            else:
                log.warning(f"⚠️ No videos found for #{hashtag}")
            
            return videos
            
        except Exception as e:
            log.error(f"❌ Error scraping hashtag #{hashtag}: {str(e)}")
            return []
    
    async def _scrape_with_ytdlp(self, url: str, limit: int) -> List[Dict]:
        """Scrape using yt-dlp"""
        try:
            # Check if yt-dlp is installed
            try:
                result = subprocess.run(
                    ['yt-dlp', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    log.warning("yt-dlp not found, falling back to manual extraction")
                    return []
            except (subprocess.TimeoutExpired, FileNotFoundError):
                log.warning("yt-dlp not installed, falling back to manual extraction")
                return []
            
            # Use yt-dlp to extract video info
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--playlist-end', str(limit),
                '--no-warnings',
                '--skip-download',
                url
            ]
            
            log.info(f"Running yt-dlp command: {' '.join(cmd)}")
            
            # Run yt-dlp
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60
            )
            
            if process.returncode != 0:
                log.error(f"yt-dlp error: {stderr.decode()}")
                return []
            
            # Parse output
            videos = []
            output = stdout.decode()
            
            for line in output.strip().split('\n'):
                if not line:
                    continue
                
                try:
                    video_info = json.loads(line)
                    parsed = self._parse_ytdlp_data(video_info)
                    if parsed:
                        videos.append(parsed)
                        if len(videos) >= limit:
                            break
                except json.JSONDecodeError:
                    continue
            
            return videos
            
        except asyncio.TimeoutError:
            log.error("yt-dlp timeout")
            return []
        except Exception as e:
            log.error(f"Error with yt-dlp: {str(e)}")
            return []
    
    def _parse_ytdlp_data(self, video_info: Dict) -> Optional[Dict]:
        """Parse video data from yt-dlp output"""
        try:
            video_id = video_info.get('id')
            if not video_id:
                return None
            
            # Extract data
            uploader = video_info.get('uploader', 'unknown')
            uploader_id = video_info.get('uploader_id', uploader)
            title = video_info.get('title', '')
            description = video_info.get('description', '')
            
            # Stats
            view_count = video_info.get('view_count', 0)
            like_count = video_info.get('like_count', 0)
            comment_count = video_info.get('comment_count', 0)
            repost_count = video_info.get('repost_count', 0)
            
            # Timestamp
            timestamp = video_info.get('timestamp')
            
            # Video URL
            video_url = video_info.get('url')
            
            # Duration
            duration = video_info.get('duration')
            
            # Hashtags
            hashtags = []
            tags = video_info.get('tags', [])
            if tags:
                hashtags = [tag.lstrip('#') for tag in tags if isinstance(tag, str)]
            
            return {
                'video_id': str(video_id),
                'url': f"https://www.tiktok.com/@{uploader_id}/video/{video_id}",
                'desc': description or title,
                'author_username': uploader_id,
                'author_nickname': uploader,
                'views': view_count or 0,
                'likes': like_count or 0,
                'comments': comment_count or 0,
                'shares': repost_count or 0,
                'created_at': timestamp,
                'hashtags': hashtags,
                'music_title': None,
                'music_author': None,
                'video_url': video_url,
                'duration': duration,
                'raw_data': video_info,
            }
            
        except Exception as e:
            log.error(f"Error parsing yt-dlp data: {str(e)}")
            return None
