"""
Test API with Rate Limiting
Run this to verify rate limiting works correctly
"""
import sys
import asyncio
import time

# Fix for Python 3.13 on Windows
if sys.platform == 'win32' and sys.version_info >= (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import httpx

API_URL = "http://localhost:8000"

async def test_rate_limiting():
    """Test that rate limiting is working"""
    print("🧪 Testing Rate Limiting...")
    print(f"Target: {API_URL}")
    print("-" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Normal request should work
        print("\n✓ Test 1: Normal request")
        try:
            response = await client.get(f"{API_URL}/health")
            print(f"  Status: {response.status_code}")
            print(f"  Headers: X-RateLimit-Limit={response.headers.get('X-RateLimit-Limit')}")
            print(f"           X-RateLimit-Remaining={response.headers.get('X-RateLimit-Remaining')}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print(f"  ⚠️  Make sure the API is running: uvicorn app.main:app --reload")
            return
        
        # Test 2: Multiple requests (should not trigger rate limit for /health)
        print("\n✓ Test 2: Multiple requests to /health (should be allowed)")
        for i in range(5):
            response = await client.get(f"{API_URL}/health")
            print(f"  Request {i+1}: {response.status_code}")
        
        # Test 3: Rapid requests to API endpoint
        print("\n✓ Test 3: Rapid requests to /api/v1/stats/health")
        success_count = 0
        rate_limited = False
        
        for i in range(10):
            try:
                response = await client.get(f"{API_URL}/api/v1/stats/health")
                if response.status_code == 200:
                    success_count += 1
                    remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
                    print(f"  Request {i+1}: ✓ Success (Remaining: {remaining})")
                elif response.status_code == 429:
                    rate_limited = True
                    data = response.json()
                    retry_after = data.get('detail', {}).get('retry_after', 'N/A')
                    print(f"  Request {i+1}: ⚠️  Rate Limited (Retry after: {retry_after}s)")
                    break
            except Exception as e:
                print(f"  Request {i+1}: ❌ Error: {e}")
            
            await asyncio.sleep(0.1)  # Small delay
        
        print(f"\n  Summary: {success_count} successful requests")
        if rate_limited:
            print(f"  ✓ Rate limiting is working correctly!")
        else:
            print(f"  ℹ️  No rate limiting triggered (limit not reached)")
    
    print("\n" + "=" * 50)
    print("✅ Rate Limiting Test Complete!")
    print("\nTo test from another device:")
    print(f"1. Make sure API is accessible: {API_URL}")
    print(f"2. From another device, run:")
    print(f"   curl {API_URL}/health")
    print(f"3. Try multiple rapid requests to trigger rate limit")

if __name__ == "__main__":
    print("=" * 50)
    print("Rate Limiting Test Suite")
    print("=" * 50)
    
    try:
        asyncio.run(test_rate_limiting())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
