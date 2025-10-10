"""
Test Monitoring - Add account and verify immediate download
"""
import asyncio
from app.scheduler.auto_scraper import auto_scraper
from app.core.logging import log


async def test_add_account():
    """Test adding account to monitoring"""
    print("=" * 60)
    print("Testing Auto Scraper - Add Account")
    print("=" * 60)
    print()
    
    # Test account
    username = "mikaylanogueira"
    
    print(f"Adding @{username} to monitoring...")
    print(f"Expected behavior:")
    print(f"  1. Add account to database")
    print(f"  2. Download latest video IMMEDIATELY")
    print(f"  3. Upload to Google Drive")
    print(f"  4. Save video ID for future checks")
    print()
    print("-" * 60)
    print()
    
    # Add account (should trigger immediate download)
    await auto_scraper.add_account(username, check_interval_minutes=60)
    
    print()
    print("=" * 60)
    print("✅ Test completed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Check logs above for '🎬 FIRST VIDEO' or '🆕 NEW VIDEO FOUND'")
    print("  2. Check downloads/profile/mikaylanogueira/ for video file")
    print("  3. Check Google Drive for uploaded video")
    print()


if __name__ == "__main__":
    asyncio.run(test_add_account())
