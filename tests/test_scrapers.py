import pytest
import asyncio
from app.scrapers.profile_scraper import ProfileScraper
from app.scrapers.hashtag_scraper import HashtagScraper


@pytest.mark.asyncio
async def test_profile_scraper_initialization():
    """Test profile scraper can be initialized"""
    async with ProfileScraper() as scraper:
        assert scraper is not None
        assert scraper.session is not None


@pytest.mark.asyncio
async def test_hashtag_scraper_initialization():
    """Test hashtag scraper can be initialized"""
    async with HashtagScraper() as scraper:
        assert scraper is not None
        assert scraper.session is not None


@pytest.mark.asyncio
async def test_profile_scraper_headers():
    """Test profile scraper generates proper headers"""
    async with ProfileScraper() as scraper:
        headers = scraper._get_headers()
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert headers["DNT"] == "1"


@pytest.mark.asyncio
async def test_video_data_parsing():
    """Test video data parsing"""
    async with ProfileScraper() as scraper:
        mock_video_data = {
            'id': '7123456789',
            'desc': 'Test video',
            'author': {
                'uniqueId': 'testuser',
                'nickname': 'Test User'
            },
            'stats': {
                'playCount': 1000,
                'diggCount': 50,
                'commentCount': 10,
                'shareCount': 5
            },
            'createTime': 1234567890,
            'challenges': [
                {'title': 'test'}
            ],
            'music': {
                'title': 'Test Music',
                'authorName': 'Test Artist'
            },
            'video': {
                'downloadAddr': 'https://example.com/video.mp4',
                'duration': 15
            }
        }
        
        parsed = scraper._parse_video_data(mock_video_data)
        
        assert parsed is not None
        assert parsed['video_id'] == '7123456789'
        assert parsed['author_username'] == 'testuser'
        assert parsed['views'] == 1000
        assert parsed['likes'] == 50
        assert 'test' in parsed['hashtags']


@pytest.mark.asyncio
async def test_date_filtering():
    """Test video date filtering"""
    from datetime import datetime, timedelta
    
    async with ProfileScraper() as scraper:
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        video = {
            'video_id': '123',
            'created_at': now.timestamp()
        }
        
        # Test since filter
        assert scraper._filter_video(video, since=yesterday, until=None) == True
        assert scraper._filter_video(video, since=tomorrow, until=None) == False
        
        # Test until filter
        assert scraper._filter_video(video, since=None, until=tomorrow) == True
        assert scraper._filter_video(video, since=None, until=yesterday) == False
