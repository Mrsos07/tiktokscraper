"""
Test complete workflow: Scrape -> Download -> Save
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.scrapers.profile_scraper import ProfileScraper
from app.scrapers.hashtag_scraper import HashtagScraper
from app.downloaders.video_downloader import VideoDownloader
from app.core.logging import log


async def test_profile_scraping(username: str = "tiktok", limit: int = 3):
    """Test profile scraping"""
    log.info(f"🧪 Testing profile scraping for @{username}")
    
    try:
        async with ProfileScraper() as scraper:
            videos = await scraper.scrape(username, limit=limit)
            
            if videos:
                log.info(f"✅ Successfully scraped {len(videos)} videos")
                for i, video in enumerate(videos, 1):
                    log.info(f"   {i}. Video ID: {video['video_id']}")
                    log.info(f"      Author: @{video['author_username']}")
                    log.info(f"      URL: {video['url']}")
                    log.info(f"      Views: {video.get('views', 0):,}")
                return videos
            else:
                log.warning("⚠️  No videos found")
                return []
                
    except Exception as e:
        log.error(f"❌ Error in profile scraping: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


async def test_hashtag_scraping(hashtag: str = "funny", limit: int = 3):
    """Test hashtag scraping"""
    log.info(f"🧪 Testing hashtag scraping for #{hashtag}")
    
    try:
        async with HashtagScraper() as scraper:
            videos = await scraper.scrape(hashtag, limit=limit)
            
            if videos:
                log.info(f"✅ Successfully scraped {len(videos)} videos")
                for i, video in enumerate(videos, 1):
                    log.info(f"   {i}. Video ID: {video['video_id']}")
                    log.info(f"      Author: @{video['author_username']}")
                    log.info(f"      URL: {video['url']}")
                return videos
            else:
                log.warning("⚠️  No videos found")
                return []
                
    except Exception as e:
        log.error(f"❌ Error in hashtag scraping: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


async def test_video_download(video_data: dict):
    """Test video download"""
    log.info(f"🧪 Testing video download for {video_data['video_id']}")
    
    try:
        output_dir = Path("./test_downloads")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{video_data['video_id']}.mp4"
        
        async with VideoDownloader() as downloader:
            result = await downloader.download_video(
                video_data,
                output_path,
                no_watermark=True
            )
            
            if result['success']:
                log.info(f"✅ Download successful!")
                log.info(f"   File size: {result['file_size']:,} bytes")
                log.info(f"   Saved to: {output_path}")
                return True
            else:
                log.error(f"❌ Download failed: {result.get('error')}")
                return False
                
    except Exception as e:
        log.error(f"❌ Error in download: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    log.info("=" * 70)
    log.info("🚀 TikTok Scraper - Full Workflow Test")
    log.info("=" * 70)
    log.info("")
    
    # Test 1: Profile Scraping
    log.info("📋 Test 1: Profile Scraping")
    log.info("-" * 70)
    profile_videos = await test_profile_scraping("tiktok", limit=2)
    log.info("")
    
    # Test 2: Hashtag Scraping
    log.info("📋 Test 2: Hashtag Scraping")
    log.info("-" * 70)
    hashtag_videos = await test_hashtag_scraping("funny", limit=2)
    log.info("")
    
    # Test 3: Video Download (if we got videos)
    if profile_videos:
        log.info("📋 Test 3: Video Download")
        log.info("-" * 70)
        await test_video_download(profile_videos[0])
        log.info("")
    
    # Summary
    log.info("=" * 70)
    log.info("📊 Test Summary")
    log.info("=" * 70)
    log.info(f"Profile videos scraped: {len(profile_videos)}")
    log.info(f"Hashtag videos scraped: {len(hashtag_videos)}")
    log.info("")
    
    if profile_videos or hashtag_videos:
        log.info("✅ Tests completed successfully!")
        log.info("")
        log.info("💡 Note: If scraping returned no videos, this might be due to:")
        log.info("   1. TikTok blocking the requests (use Playwright fallback)")
        log.info("   2. Rate limiting (wait a few minutes)")
        log.info("   3. Invalid username/hashtag")
        log.info("   4. Network issues")
    else:
        log.warning("⚠️  No videos were scraped. Check the logs above for errors.")
    
    log.info("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("\n\n👋 Test interrupted by user")
    except Exception as e:
        log.error(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
