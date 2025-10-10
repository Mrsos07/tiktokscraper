"""
Direct test of ReliableScraper to diagnose the issue
"""
import asyncio
import sys
from app.scrapers.reliable_scraper import ReliableTikTokScraper

async def test_scraper():
    print("=" * 60)
    print("Testing ReliableScraper directly")
    print("=" * 60)
    print()
    
    username = "mikaylanogueira"
    limit = 2
    
    print(f"Target: @{username}")
    print(f"Limit: {limit} videos")
    print()
    
    try:
        print("Initializing scraper...")
        async with ReliableTikTokScraper() as scraper:
            print("✅ Scraper initialized")
            print()
            
            print("Starting scrape...")
            videos = await scraper.scrape_profile(username, limit)
            
            print()
            print("=" * 60)
            print(f"Results: Found {len(videos)} videos")
            print("=" * 60)
            print()
            
            if videos:
                for i, video in enumerate(videos, 1):
                    print(f"Video {i}:")
                    print(f"  ID: {video['video_id']}")
                    print(f"  URL: {video['url']}")
                    print(f"  Author: @{video['author_username']}")
                    print(f"  Download URL: {video['video_url'][:50] if video['video_url'] else 'N/A'}...")
                    print()
            else:
                print("⚠️ No videos found!")
                print()
                print("Possible reasons:")
                print("1. Chromium not installed properly")
                print("2. TikTok blocking the scraper")
                print("3. Username doesn't exist or is private")
                print("4. Network/connection issues")
                
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(test_scraper())
    sys.exit(exit_code)
