"""
Basic usage examples for TikTok Scraper API
"""
import requests
import time
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-key-here"  # Optional, if API key authentication is enabled

# Headers
headers = {
    "Content-Type": "application/json",
}

# Add API key if configured
if API_KEY and API_KEY != "your-api-key-here":
    headers["X-API-Key"] = API_KEY


def create_profile_job(username: str, limit: int = 50, no_watermark: bool = True):
    """Create a job to scrape videos from a profile"""
    print(f"\n📱 Creating job to scrape @{username}...")
    
    payload = {
        "mode": "profile",
        "value": username,
        "limit": limit,
        "no_watermark": no_watermark
    }
    
    response = requests.post(f"{API_BASE_URL}/jobs", json=payload, headers=headers)
    
    if response.status_code == 201:
        job = response.json()
        print(f"✅ Job created successfully!")
        print(f"   Job ID: {job['id']}")
        print(f"   Status: {job['status']}")
        return job['id']
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None


def create_hashtag_job(hashtag: str, limit: int = 50, no_watermark: bool = True):
    """Create a job to scrape videos from a hashtag"""
    print(f"\n#️⃣ Creating job to scrape #{hashtag}...")
    
    payload = {
        "mode": "hashtag",
        "value": hashtag,
        "limit": limit,
        "no_watermark": no_watermark
    }
    
    response = requests.post(f"{API_BASE_URL}/jobs", json=payload, headers=headers)
    
    if response.status_code == 201:
        job = response.json()
        print(f"✅ Job created successfully!")
        print(f"   Job ID: {job['id']}")
        print(f"   Status: {job['status']}")
        return job['id']
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None


def check_job_status(job_id: str):
    """Check the status of a job"""
    response = requests.get(f"{API_BASE_URL}/jobs/{job_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        job = data['job']
        
        print(f"\n📊 Job Status:")
        print(f"   Status: {job['status']}")
        print(f"   Progress: {job['progress']}%")
        print(f"   Total Videos: {job['total_videos']}")
        print(f"   Successful: {job['successful_downloads']}")
        print(f"   Failed: {job['failed_downloads']}")
        
        return job
    else:
        print(f"❌ Error: {response.status_code}")
        return None


def wait_for_job_completion(job_id: str, check_interval: int = 5):
    """Wait for a job to complete"""
    print(f"\n⏳ Waiting for job {job_id} to complete...")
    
    while True:
        job = check_job_status(job_id)
        
        if not job:
            break
        
        if job['status'] in ['completed', 'failed', 'cancelled']:
            print(f"\n✅ Job {job['status']}!")
            break
        
        time.sleep(check_interval)
    
    return job


def get_job_videos(job_id: str):
    """Get all videos from a job"""
    response = requests.get(f"{API_BASE_URL}/jobs/{job_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        videos = data['videos']
        drive_links = data['drive_links']
        
        print(f"\n🎬 Videos ({len(videos)}):")
        
        for i, video in enumerate(videos[:5], 1):  # Show first 5
            print(f"\n   {i}. Video ID: {video['id']}")
            print(f"      Author: @{video['author_username']}")
            print(f"      Views: {video['views']:,}")
            print(f"      Likes: {video['likes']:,}")
            print(f"      Status: {video['status']}")
            
            # Find Drive link
            drive_link = next((link for link in drive_links if link['video_id'] == video['id']), None)
            if drive_link:
                print(f"      Drive: {drive_link['video_link']}")
        
        if len(videos) > 5:
            print(f"\n   ... and {len(videos) - 5} more videos")
        
        return videos, drive_links
    else:
        print(f"❌ Error: {response.status_code}")
        return [], []


def list_all_jobs(limit: int = 10):
    """List all jobs"""
    print(f"\n📋 Listing jobs...")
    
    response = requests.get(f"{API_BASE_URL}/jobs?limit={limit}", headers=headers)
    
    if response.status_code == 200:
        jobs = response.json()
        
        print(f"\n   Found {len(jobs)} jobs:")
        
        for i, job in enumerate(jobs, 1):
            print(f"\n   {i}. {job['mode'].upper()}: {job['value']}")
            print(f"      Status: {job['status']} ({job['progress']}%)")
            print(f"      Videos: {job['successful_downloads']}/{job['total_videos']}")
            print(f"      Created: {job['created_at'][:19]}")
        
        return jobs
    else:
        print(f"❌ Error: {response.status_code}")
        return []


def get_system_stats():
    """Get system statistics"""
    print(f"\n📊 System Statistics:")
    
    response = requests.get(f"{API_BASE_URL}/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        
        print(f"\n   Jobs:")
        print(f"      Total: {stats['total_jobs']}")
        print(f"      Pending: {stats['pending_jobs']}")
        print(f"      Running: {stats['running_jobs']}")
        print(f"      Completed: {stats['completed_jobs']}")
        print(f"      Failed: {stats['failed_jobs']}")
        
        print(f"\n   Videos:")
        print(f"      Total: {stats['total_videos']}")
        print(f"      Downloaded: {stats['downloaded_videos']}")
        print(f"      Uploaded: {stats['uploaded_videos']}")
        print(f"      Failed: {stats['failed_videos']}")
        
        storage_gb = stats['total_storage_bytes'] / (1024**3)
        print(f"\n   Storage: {storage_gb:.2f} GB")
        
        return stats
    else:
        print(f"❌ Error: {response.status_code}")
        return None


def create_scheduled_job(name: str, mode: str, value: str, interval_minutes: int = 1440):
    """Create a scheduled recurring job"""
    print(f"\n⏰ Creating scheduled job: {name}...")
    
    payload = {
        "name": name,
        "mode": mode,
        "value": value,
        "limit": 50,
        "interval_minutes": interval_minutes,
        "no_watermark": True,
        "enabled": True
    }
    
    response = requests.post(f"{API_BASE_URL}/scheduled-jobs", json=payload, headers=headers)
    
    if response.status_code == 201:
        job = response.json()
        print(f"✅ Scheduled job created!")
        print(f"   ID: {job['id']}")
        print(f"   Interval: Every {interval_minutes} minutes")
        return job['id']
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("TikTok Scraper - Basic Usage Examples")
    print("=" * 60)
    
    # Example 1: Get system stats
    get_system_stats()
    
    # Example 2: Create a profile scraping job
    job_id = create_profile_job("khaby.lame", limit=10, no_watermark=True)
    
    if job_id:
        # Wait for job to complete
        job = wait_for_job_completion(job_id, check_interval=5)
        
        # Get videos from the job
        if job and job['status'] == 'completed':
            videos, drive_links = get_job_videos(job_id)
    
    # Example 3: Create a hashtag scraping job
    # job_id = create_hashtag_job("funny", limit=10)
    
    # Example 4: List all jobs
    list_all_jobs(limit=5)
    
    # Example 5: Create a scheduled job (runs daily)
    # scheduled_id = create_scheduled_job(
    #     name="Daily Scrape - @username",
    #     mode="profile",
    #     value="username",
    #     interval_minutes=1440  # 24 hours
    # )
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
