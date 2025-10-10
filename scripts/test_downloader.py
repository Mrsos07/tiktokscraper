"""
Test video downloader
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.downloaders.video_downloader import VideoDownloader
from app.core.logging import log


async def test_download(video_url: str, output_path: str, no_watermark: bool = True):
    """Test video download"""
    log.info(f"Testing video download from: {video_url}")
    
    try:
        # Create mock video data
        video_data = {
            'video_id': 'test_video',
            'url': video_url,
            'video_url': None  # Will be extracted
        }
        
        output = Path(output_path)
        
        async with VideoDownloader() as downloader:
            result = await downloader.download_video(
                video_data,
                output,
                no_watermark=no_watermark
            )
            
            if result['success']:
                log.info("✅ Download successful!")
                log.info(f"  File size: {result['file_size']:,} bytes")
                log.info(f"  Has watermark: {result.get('has_watermark', 'Unknown')}")
                log.info(f"  Local path: {result.get('local_path')}")
            else:
                log.error(f"❌ Download failed: {result.get('error')}")
            
            return result
            
    except Exception as e:
        log.error(f"Error testing downloader: {str(e)}")
        return {'success': False, 'error': str(e)}


async def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test video downloader")
    parser.add_argument("--url", required=True, help="TikTok video URL")
    parser.add_argument("--output", default="./test_download.mp4", help="Output file path")
    parser.add_argument("--no-watermark", action="store_true", help="Attempt no-watermark download")
    
    args = parser.parse_args()
    
    await test_download(args.url, args.output, args.no_watermark)


if __name__ == "__main__":
    asyncio.run(main())
