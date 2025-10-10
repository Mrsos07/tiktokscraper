import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_stats_endpoint():
    """Test stats endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_jobs" in data
        assert "total_videos" in data


@pytest.mark.asyncio
async def test_create_job_validation():
    """Test job creation validation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Invalid mode
        response = await client.post("/api/v1/jobs", json={
            "mode": "invalid",
            "value": "test",
            "limit": 10
        })
        assert response.status_code == 422
        
        # Missing value
        response = await client.post("/api/v1/jobs", json={
            "mode": "profile",
            "limit": 10
        })
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_jobs():
    """Test listing jobs"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/jobs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_videos():
    """Test listing videos"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/videos")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "videos" in data
        assert isinstance(data["videos"], list)
