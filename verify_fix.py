"""
Verify Rate Limiting Fix
تحقق من أن الحل يعمل بشكل صحيح
"""
import sys
import os

print("=" * 60)
print("التحقق من حل مشكلة Too Many Requests")
print("=" * 60)

# Check 1: Middleware file exists
print("\n1. التحقق من وجود ملف Middleware...")
middleware_path = "app/middleware/rate_limiter.py"
if os.path.exists(middleware_path):
    print(f"   ✓ {middleware_path} موجود")
else:
    print(f"   ✗ {middleware_path} غير موجود")
    sys.exit(1)

# Check 2: __init__ file exists
print("\n2. التحقق من ملف __init__.py...")
init_path = "app/middleware/__init__.py"
if os.path.exists(init_path):
    print(f"   ✓ {init_path} موجود")
else:
    print(f"   ✗ {init_path} غير موجود")
    sys.exit(1)

# Check 3: Import middleware
print("\n3. اختبار استيراد Middleware...")
try:
    from app.middleware import RateLimitMiddleware
    print("   ✓ تم استيراد RateLimitMiddleware بنجاح")
except ImportError as e:
    print(f"   ✗ فشل الاستيراد: {e}")
    sys.exit(1)

# Check 4: Check config
print("\n4. التحقق من الإعدادات...")
try:
    from app.core.config import settings
    print(f"   ✓ RATE_LIMIT_REQUESTS_PER_MINUTE: {settings.RATE_LIMIT_REQUESTS_PER_MINUTE}")
    print(f"   ✓ RATE_LIMIT_BURST: {settings.RATE_LIMIT_BURST}")
except Exception as e:
    print(f"   ✗ فشل تحميل الإعدادات: {e}")
    sys.exit(1)

# Check 5: Verify main.py has middleware
print("\n5. التحقق من main.py...")
try:
    with open("app/main.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "from app.middleware import RateLimitMiddleware" in content:
            print("   ✓ تم استيراد RateLimitMiddleware في main.py")
        else:
            print("   ✗ لم يتم استيراد RateLimitMiddleware في main.py")
            sys.exit(1)
        
        if "app.add_middleware(RateLimitMiddleware" in content or "app.add_middleware(\n    RateLimitMiddleware" in content:
            print("   ✓ تم إضافة RateLimitMiddleware إلى التطبيق")
        else:
            print("   ✗ لم يتم إضافة RateLimitMiddleware إلى التطبيق")
            sys.exit(1)
except Exception as e:
    print(f"   ✗ فشل قراءة main.py: {e}")
    sys.exit(1)

# Check 6: Test middleware instantiation
print("\n6. اختبار إنشاء Middleware...")
try:
    from fastapi import FastAPI
    app = FastAPI()
    middleware = RateLimitMiddleware(app, requests_per_minute=60, burst=100)
    print("   ✓ تم إنشاء Middleware بنجاح")
    print(f"   ✓ Requests per minute: {middleware.requests_per_minute}")
    print(f"   ✓ Burst limit: {middleware.burst}")
except Exception as e:
    print(f"   ✗ فشل إنشاء Middleware: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ جميع الفحوصات نجحت!")
print("=" * 60)
print("\nالخطوات التالية:")
print("1. شغل الخادم: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
print("2. اختبر من جهاز آخر: curl http://YOUR_IP:8000/health")
print("3. جرب طلبات كثيرة بسرعة لاختبار Rate Limiting")
print("\nملاحظة: راجع ملف TEST_RATE_LIMIT.md لتعليمات الاختبار التفصيلية")
