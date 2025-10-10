"""
Quick API test - Create a test job
"""
import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get("http://127.0.0.1:8000/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

def test_stats():
    """Test stats endpoint"""
    print("📊 Testing stats endpoint...")
    response = requests.get(f"{API_URL}/stats")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"   Total Jobs: {stats['total_jobs']}")
        print(f"   Total Videos: {stats['total_videos']}")
    print()

def test_create_job():
    """Test job creation"""
    print("➕ Testing job creation...")
    
    payload = {
        "mode": "profile",
        "value": "test_user",
        "limit": 5,
        "no_watermark": True
    }
    
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{API_URL}/jobs", json=payload)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        job = response.json()
        print(f"   ✅ Job created successfully!")
        print(f"   Job ID: {job['id']}")
        print(f"   Mode: {job['mode']}")
        print(f"   Value: {job['value']}")
        print(f"   Status: {job['status']}")
        return job['id']
    else:
        print(f"   ❌ Error: {response.text}")
        return None
    print()

def test_list_jobs():
    """Test listing jobs"""
    print("📋 Testing list jobs...")
    response = requests.get(f"{API_URL}/jobs?limit=5")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        jobs = response.json()
        print(f"   Found {len(jobs)} jobs")
        for job in jobs:
            print(f"   - {job['mode']}: {job['value']} ({job['status']})")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TikTok Scraper API - Quick Test")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_stats()
        test_create_job()
        test_list_jobs()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API server")
        print("   Make sure the server is running:")
        print("   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
