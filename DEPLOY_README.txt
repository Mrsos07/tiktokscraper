========================================
     TIKTOK SCRAPER - DEPLOYMENT
========================================

تم إنشاء ملفات الـ Deployment بنجاح!

الملفات المتوفرة:
------------------
✓ Dockerfile              - صورة Docker للتطبيق
✓ docker-compose.yml      - إعدادات الخدمات
✓ .dockerignore          - ملفات يتم تجاهلها
✓ DEPLOY.ps1             - نشر التطبيق
✓ STOP.ps1               - إيقاف الخدمات
✓ UPDATE.ps1             - تحديث وإعادة النشر
✓ LOGS.ps1               - عرض السجلات
✓ HEALTH_CHECK.ps1       - فحص صحة الخدمات


خطوات النشر:
-------------

1. تثبيت Docker Desktop:
   https://www.docker.com/products/docker-desktop

2. وضع ملف credentials.json:
   نسخ الملف إلى: .\credentials\credentials.json

3. تشغيل الأمر:
   .\DEPLOY.ps1

4. الوصول للخدمات:
   API:       http://localhost:8000/docs
   Dashboard: http://localhost:8501


الأوامر المتاحة:
-----------------

.\DEPLOY.ps1           - بناء وتشغيل جميع الخدمات
.\STOP.ps1             - إيقاف الخدمات
.\UPDATE.ps1           - تحديث الكود وإعادة التشغيل
.\LOGS.ps1             - عرض سجلات جميع الخدمات
.\LOGS.ps1 api         - عرض سجلات API فقط
.\LOGS.ps1 dashboard   - عرض سجلات Dashboard فقط
.\HEALTH_CHECK.ps1     - فحص صحة الخدمات


الخدمات المتوفرة:
------------------

1. API Server (Port 8000)
   - FastAPI application
   - Auto monitoring system
   - Video scraping & downloading
   - Google Drive integration

2. Dashboard (Port 8501)
   - Streamlit web interface
   - Monitor accounts
   - View videos
   - Manage jobs


المميزات:
----------

✓ رفع تلقائي للفيديوهات الجديدة فقط
✓ توليد ترجمة عربية تلقائياً
✓ رفع نسختين (أصلي + مترجم)
✓ منع التكرار في الرفع
✓ مراقبة تلقائية للحسابات
✓ إعادة تشغيل تلقائي عند الأخطاء


الملفات المهمة:
----------------

./downloads/           - الفيديوهات المحملة
./logs/               - سجلات التطبيق
./credentials/        - بيانات Google Drive
./tiktok_scraper.db   - قاعدة البيانات


استكشاف الأخطاء:
-----------------

1. المنفذ مستخدم:
   - تغيير المنافذ في docker-compose.yml

2. فشل البناء:
   - تشغيل: .\UPDATE.ps1

3. الخدمة لا تعمل:
   - فحص السجلات: .\LOGS.ps1
   - فحص الحالة: .\HEALTH_CHECK.ps1

4. مشاكل Google Drive:
   - التأكد من وجود credentials.json
   - التأكد من الصلاحيات


ملاحظات مهمة:
--------------

• يجب وجود credentials.json قبل التشغيل
• ffmpeg مثبت تلقائياً للترجمة
• النظام يحفظ drive_file_id لمنع التكرار
• الفيديوهات تُرفع مرة واحدة فقط
• النسخة المترجمة تُرفع تلقائياً


للدعم:
-------

1. فحص السجلات أولاً: .\LOGS.ps1
2. فحص الصحة: .\HEALTH_CHECK.ps1
3. مراجعة: DEPLOYMENT_GUIDE.txt
