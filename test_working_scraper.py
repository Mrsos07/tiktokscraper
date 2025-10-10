"""
Test WorkingScraper directly
"""
import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from app.scrapers.working_scraper import WorkingScraper


async def main():
    print("=" * 60)
    print("Testing WorkingScraper")
    print("=" * 60)
    print()
    
    username = "mikaylanogueira"
    limit = 1
    
    print(f"Username: {username}")
    print(f"Limit: {limit}")
    print()
    
    try:
        async with WorkingScraper() as scraper:
            results = await scraper.scrape_and_download(username, limit)
            
            print()
            print("=" * 60)
            print(f"Results: {len(results)} videos")
            print("=" * 60)
            
            for i, result in enumerate(results, 1):
                print(f"\nVideo {i}:")
                print(f"  ID: {result['video_id']}")
                print(f"  URL: {result['url']}")
                print(f"  Success: {result['success']}")
                if result['success']:
                    print(f"  File: {result['file_path']}")
                    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
