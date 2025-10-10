"""
Test scraper functionality
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scrapers.profile_scraper import ProfileScraper
from app.scrapers.hashtag_scraper import HashtagScraper
from app.core.logging import log


async def test_profile_scraper(username: str, limit: int = 5):
    """Test profile scraper"""
    log.info(f"Testing profile scraper for @{username}")
    
    try:
        async with ProfileScraper() as scraper:
            videos = await scraper.scrape(username, limit=limit)
            
            log.info(f"Found {len(videos)} videos")
            
            for i, video in enumerate(videos, 1):
                log.info(f"\nVideo {i}:")
                log.info(f"  ID: {video['video_id']}")
                log.info(f"  URL: {video['url']}")
                log.info(f"  Author: {video['author_username']}")
                log.info(f"  Description: {video.get('desc', 'N/A')[:100]}")
                log.info(f"  Views: {video.get('views', 0):,}")
                log.info(f"  Likes: {video.get('likes', 0):,}")
            
            return videos
            
    except Exception as e:
        log.error(f"Error testing profile scraper: {str(e)}")
        return []


async def test_hashtag_scraper(hashtag: str, limit: int = 5):
    """Test hashtag scraper"""
    log.info(f"Testing hashtag scraper for #{hashtag}")
    
    try:
        async with HashtagScraper() as scraper:
            videos = await scraper.scrape(hashtag, limit=limit)
            
            log.info(f"Found {len(videos)} videos")
            
            for i, video in enumerate(videos, 1):
                log.info(f"\nVideo {i}:")
                log.info(f"  ID: {video['video_id']}")
                log.info(f"  URL: {video['url']}")
                log.info(f"  Author: {video['author_username']}")
                log.info(f"  Description: {video.get('desc', 'N/A')[:100]}")
                log.info(f"  Views: {video.get('views', 0):,}")
                log.info(f"  Likes: {video.get('likes', 0):,}")
            
            return videos
            
    except Exception as e:
        log.error(f"Error testing hashtag scraper: {str(e)}")
        return []


async def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test TikTok scraper")
    parser.add_argument("--mode", choices=["profile", "hashtag"], required=True, help="Scraping mode")
    parser.add_argument("--value", required=True, help="Username or hashtag")
    parser.add_argument("--limit", type=int, default=5, help="Number of videos to scrape")
    
    args = parser.parse_args()
    
    if args.mode == "profile":
        await test_profile_scraper(args.value, args.limit)
    else:
        await test_hashtag_scraper(args.value, args.limit)


if __name__ == "__main__":
    asyncio.run(main())
