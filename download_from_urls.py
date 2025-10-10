"""
Download videos from URLs - Manual method
User copies video URLs from TikTok and pastes them here
"""
import asyncio
from app.scrapers.hashtag_url_scraper import download_from_urls


# ✏️ PASTE YOUR VIDEO URLS HERE:
VIDEO_URLS = [
    "https://www.tiktok.com/@username/video/1234567890",
    "https://www.tiktok.com/@username/video/9876543210",
    # Add more URLs...
]

CATEGORY = "beauty"  # or "fashion", "food", etc.


async def main():
    print("=" * 60)
    print("Downloading Videos from URLs")
    print("=" * 60)
    print()
    print(f"Category: {CATEGORY}")
    print(f"Total URLs: {len(VIDEO_URLS)}")
    print()
    
    if not VIDEO_URLS or VIDEO_URLS[0] == "https://www.tiktok.com/@username/video/1234567890":
        print("⚠️ Please edit this file and add your video URLs!")
        print()
        print("Steps:")
        print("1. Go to https://www.tiktok.com/explore")
        print("2. Click on 'Beauty & Care' (الجمال والعناية)")
        print("3. Right-click on videos and copy link")
        print("4. Paste links in VIDEO_URLS list above")
        print("5. Run this script again")
        return
    
    videos = await download_from_urls(VIDEO_URLS, CATEGORY, len(VIDEO_URLS))
    
    print()
    print("=" * 60)
    print(f"✅ Downloaded {len(videos)} videos!")
    print("=" * 60)
    
    for i, video in enumerate(videos, 1):
        print(f"\n{i}. Video ID: {video['video_id']}")
        print(f"   File: {video['video_url']}")


if __name__ == "__main__":
    asyncio.run(main())
