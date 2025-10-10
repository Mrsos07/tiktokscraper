"""
Test Explore Scraper
"""
import asyncio
from app.scrapers.explore_scraper import download_explore_videos


async def main():
    print("=" * 60)
    print("Testing Explore Scraper")
    print("=" * 60)
    print()
    
    # Test with beauty category (الجمال والعناية)
    category = "beauty"  # or "الجمال" for Arabic
    limit = 3
    
    print(f"Downloading {limit} videos from Explore category: {category}")
    print()
    
    videos = await download_explore_videos(category, limit)
    
    print()
    print("=" * 60)
    print(f"Results: {len(videos)} videos downloaded")
    print("=" * 60)
    
    for i, video in enumerate(videos, 1):
        print(f"\n{i}. Video ID: {video['video_id']}")
        print(f"   Author: @{video['author_username']}")
        print(f"   File: {video['video_url']}")


if __name__ == "__main__":
    asyncio.run(main())
