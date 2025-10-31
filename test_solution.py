"""
اختبار سريع للحل - Test Rate Limiting Solution
"""
import asyncio
import sys

# Fix for Windows Python 3.13
if sys.platform == 'win32' and sys.version_info >= (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print("=" * 60)
print("اختبار حل مشكلة Too Many Requests")
print("=" * 60)

# Test 1: Import middleware
print("\n[1/4] اختبار استيراد Middleware...")
try:
    from app.middleware import RateLimitMiddleware
    print("      ✓ نجح")
except Exception as e:
    print(f"      ✗ فشل: {e}")
    sys.exit(1)

# Test 2: Import config
print("\n[2/4] اختبار الإعدادات...")
try:
    from app.core.config import settings
    print(f"      ✓ Requests/min: {settings.RATE_LIMIT_REQUESTS_PER_MINUTE}")
    print(f"      ✓ Burst limit: {settings.RATE_LIMIT_BURST}")
except Exception as e:
    print(f"      ✗ فشل: {e}")
    sys.exit(1)

# Test 3: Create middleware instance
print("\n[3/4] اختبار إنشاء Middleware...")
try:
    from fastapi import FastAPI
    app = FastAPI()
    middleware = RateLimitMiddleware(app)
    print(f"      ✓ تم الإنشاء بنجاح")
except Exception as e:
    print(f"      ✗ فشل: {e}")
    sys.exit(1)

# Test 4: Check main.py
print("\n[4/4] التحقق من main.py...")
try:
    with open("app/main.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "RateLimitMiddleware" in content and "app.add_middleware" in content:
            print("      ✓ Middleware مفعل في main.py")
        else:
            print("      ✗ Middleware غير مفعل")
            sys.exit(1)
except Exception as e:
    print(f"      ✗ فشل: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ جميع الاختبارات نجحت!")
print("=" * 60)
print("\nالخطوات التالية:")
print("1. شغل الخادم:")
print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
print("\n2. اختبر من جهاز آخر:")
print("   curl http://YOUR_IP:8000/health")
print("\n3. لاختبار Rate Limiting:")
print("   python test_api_with_rate_limit.py")
print("\n📄 للمزيد من التفاصيل: راجع SOLUTION_SUMMARY.md")
