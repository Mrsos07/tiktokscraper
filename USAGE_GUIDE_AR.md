# 📖 دليل الاستخدام الكامل - TikTok Scraper

## 🎯 نظرة عامة

هذا النظام يتيح لك:
- ✅ جلب فيديوهات من ملف شخصي TikTok
- ✅ جلب فيديوهات من هاشتاق معين
- ✅ تحميل الفيديوهات بدون علامة مائية (إن أمكن)
- ✅ رفع تلقائي إلى Google Drive
- ✅ جدولة مهام دورية

---

## 🚀 البدء السريع

### 1. تشغيل الخادم

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. فتح واجهة API

افتح المتصفح وانتقل إلى: **http://127.0.0.1:8000/docs**

---

## 📝 إنشاء مهمة جديدة

### الطريقة 1: عبر Swagger UI (الأسهل)

1. افتح http://127.0.0.1:8000/docs
2. ابحث عن **POST /api/v1/jobs**
3. انقر على **Try it out**
4. أدخل البيانات:

#### مثال 1: جلب من ملف شخصي
```json
{
  "mode": "profile",
  "value": "tiktok",
  "limit": 10,
  "no_watermark": true
}
```

#### مثال 2: جلب من هاشتاق
```json
{
  "mode": "hashtag",
  "value": "funny",
  "limit": 20,
  "no_watermark": true
}
```

5. انقر على **Execute**
6. ستحصل على **Job ID** - احتفظ به!

### الطريقة 2: عبر Python

```python
import requests

# إنشاء مهمة
response = requests.post("http://127.0.0.1:8000/api/v1/jobs", json={
    "mode": "profile",
    "value": "tiktok",
    "limit": 10,
    "no_watermark": True
})

job = response.json()
job_id = job['id']
print(f"✅ تم إنشاء المهمة: {job_id}")
```

### الطريقة 3: عبر cURL

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/jobs" ^
  -H "Content-Type: application/json" ^
  -d "{\"mode\":\"profile\",\"value\":\"tiktok\",\"limit\":10,\"no_watermark\":true}"
```

---

## 🔍 متابعة حالة المهمة

### عبر Swagger UI

1. افتح http://127.0.0.1:8000/docs
2. ابحث عن **GET /api/v1/jobs/{job_id}**
3. أدخل Job ID
4. انقر على **Execute**

### عبر Python

```python
import requests
import time

job_id = "YOUR_JOB_ID_HERE"

while True:
    response = requests.get(f"http://127.0.0.1:8000/api/v1/jobs/{job_id}")
    job = response.json()['job']
    
    print(f"الحالة: {job['status']}")
    print(f"التقدم: {job['progress']}%")
    print(f"الفيديوهات: {job['successful_downloads']}/{job['total_videos']}")
    
    if job['status'] in ['completed', 'failed']:
        break
    
    time.sleep(5)  # انتظر 5 ثواني

print("✅ المهمة انتهت!")
```

---

## 📊 حالات المهمة

| الحالة | الوصف |
|--------|-------|
| `pending` | في الانتظار |
| `running` | قيد التنفيذ |
| `completed` | اكتملت بنجاح |
| `failed` | فشلت |
| `cancelled` | تم إلغاؤها |

---

## 🎬 عرض الفيديوهات المحملة

### عبر API

```bash
curl "http://127.0.0.1:8000/api/v1/videos?limit=20"
```

### عبر Python

```python
import requests

response = requests.get("http://127.0.0.1:8000/api/v1/videos", params={
    "mode": "profile",
    "value": "tiktok",
    "limit": 20
})

videos = response.json()['videos']

for video in videos:
    print(f"📹 {video['id']}")
    print(f"   المؤلف: @{video['author_username']}")
    print(f"   المشاهدات: {video['views']:,}")
    print(f"   الحالة: {video['status']}")
    if video['drive_file_id']:
        print(f"   🔗 Drive: https://drive.google.com/file/d/{video['drive_file_id']}/view")
    print()
```

---

## ⏰ جدولة مهام دورية

### إنشاء مهمة مجدولة

```json
{
  "name": "جلب يومي - @username",
  "mode": "profile",
  "value": "username",
  "limit": 50,
  "interval_minutes": 1440,
  "no_watermark": true,
  "enabled": true
}
```

**ملاحظة**: `interval_minutes: 1440` = مرة كل 24 ساعة

### عبر Swagger UI

1. افتح http://127.0.0.1:8000/docs
2. ابحث عن **POST /api/v1/scheduled-jobs**
3. أدخل البيانات أعلاه
4. انقر على **Execute**

---

## 📁 مكان حفظ الفيديوهات

### محلياً (مؤقت)
```
downloads/
├── profile/
│   └── username/
│       └── video_id.mp4
└── hashtag/
    └── tagname/
        └── video_id.mp4
```

### Google Drive (دائم)
```
/TikTok/
├── profile/
│   └── username/
│       └── 2025/
│           └── 01/
│               ├── video_id.mp4
│               └── video_id_metadata.json
└── hashtag/
    └── tagname/
        └── 2025/
            └── 01/
                ├── video_id.mp4
                └── video_id_metadata.json
```

---

## 🔧 خيارات متقدمة

### تحديد فترة زمنية

```json
{
  "mode": "profile",
  "value": "username",
  "limit": 100,
  "since": "2024-01-01T00:00:00Z",
  "until": "2024-12-31T23:59:59Z",
  "no_watermark": true
}
```

### تحديد مجلد Google Drive

```json
{
  "mode": "profile",
  "value": "username",
  "limit": 50,
  "drive_folder_id": "YOUR_FOLDER_ID_HERE",
  "no_watermark": true
}
```

---

## 🎨 استخدام لوحة التحكم (Streamlit)

### تشغيل لوحة التحكم

```bash
streamlit run admin/dashboard.py
```

ثم افتح: **http://localhost:8501**

### الميزات:
- ✅ عرض الإحصائيات في الوقت الفعلي
- ✅ إنشاء مهام جديدة بسهولة
- ✅ مراقبة المهام الجارية
- ✅ عرض الفيديوهات المحملة
- ✅ إدارة المهام المجدولة

---

## 🐛 حل المشاكل الشائعة

### المشكلة 1: لا يتم جلب فيديوهات

**الأسباب المحتملة:**
- اسم المستخدم أو الهاشتاق غير صحيح
- TikTok يحجب الطلبات
- الحساب خاص
- مشاكل في الشبكة

**الحلول:**
1. تأكد من صحة اسم المستخدم (بدون @)
2. تأكد من أن الحساب عام
3. انتظر قليلاً ثم حاول مرة أخرى
4. تحقق من السجلات في `logs/`

### المشكلة 2: فشل التحميل

**الحلول:**
1. تحقق من اتصال الإنترنت
2. تحقق من مساحة القرص
3. حاول مرة أخرى عبر:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/videos/{video_id}/retry"
```

### المشكلة 3: خطأ في Google Drive

**الحلول:**
1. تأكد من إعداد OAuth:
```bash
python scripts/setup_google_drive.py
```
2. تحقق من صلاحية Token
3. تحقق من مساحة Google Drive

---

## 📊 عرض الإحصائيات

```bash
curl "http://127.0.0.1:8000/api/v1/stats"
```

**النتيجة:**
```json
{
  "total_jobs": 10,
  "pending_jobs": 1,
  "running_jobs": 2,
  "completed_jobs": 7,
  "failed_jobs": 0,
  "total_videos": 150,
  "downloaded_videos": 140,
  "uploaded_videos": 135,
  "failed_videos": 10,
  "total_storage_bytes": 5242880000,
  "scheduled_jobs_count": 3,
  "active_scheduled_jobs": 2
}
```

---

## 🔐 الأمان والخصوصية

### ⚠️ تنبيهات مهمة:

1. **المحتوى العام فقط**: النظام يجلب المحتوى العام فقط
2. **احترام الحقوق**: احترم حقوق المؤلفين
3. **الاستخدام الأخلاقي**: استخدم النظام بشكل أخلاقي
4. **حدود المعدل**: لا تفرط في الطلبات

### 🛡️ الإعدادات الموصى بها:

```env
# في ملف .env
TIKTOK_REQUEST_DELAY_MIN=3
TIKTOK_REQUEST_DELAY_MAX=7
RATE_LIMIT_REQUESTS_PER_MINUTE=5
```

---

## 📞 الحصول على المساعدة

### السجلات

```bash
# عرض السجلات
type logs\app_2025-10-09.log

# عرض الأخطاء فقط
type logs\errors_2025-10-09.log
```

### الاختبار

```bash
# اختبار السكرابر
python scripts/test_scraper.py --mode profile --value tiktok --limit 3

# اختبار API
python test_api_quick.py

# اختبار كامل
python test_full_workflow.py
```

---

## 💡 نصائح للاستخدام الأمثل

1. **ابدأ بعدد قليل**: جرب 5-10 فيديوهات أولاً
2. **راقب السجلات**: تابع `logs/` لمعرفة ما يحدث
3. **استخدم الجدولة**: للمهام الدورية
4. **نظف التخزين**: احذف الملفات المحلية بعد الرفع
5. **احترم الحدود**: لا تفرط في الطلبات

---

## 🎓 أمثلة عملية

### مثال 1: جلب آخر 50 فيديو من مستخدم

```python
import requests

response = requests.post("http://127.0.0.1:8000/api/v1/jobs", json={
    "mode": "profile",
    "value": "username",
    "limit": 50,
    "no_watermark": True
})

print(f"Job ID: {response.json()['id']}")
```

### مثال 2: جلب فيديوهات هاشتاق شهير

```python
import requests

response = requests.post("http://127.0.0.1:8000/api/v1/jobs", json={
    "mode": "hashtag",
    "value": "viral",
    "limit": 30,
    "no_watermark": True
})

print(f"Job ID: {response.json()['id']}")
```

### مثال 3: جدولة جلب يومي

```python
import requests

response = requests.post("http://127.0.0.1:8000/api/v1/scheduled-jobs", json={
    "name": "جلب يومي - @username",
    "mode": "profile",
    "value": "username",
    "limit": 50,
    "interval_minutes": 1440,  # كل 24 ساعة
    "no_watermark": True,
    "enabled": True
})

print(f"Scheduled Job ID: {response.json()['id']}")
```

---

## ✅ قائمة التحقق السريعة

قبل البدء، تأكد من:

- [ ] الخادم يعمل على http://127.0.0.1:8000
- [ ] يمكنك الوصول إلى http://127.0.0.1:8000/docs
- [ ] قاعدة البيانات مهيأة
- [ ] Playwright مثبت (`playwright install chromium`)
- [ ] المكتبات المطلوبة مثبتة
- [ ] (اختياري) Google Drive معد

---

**🎉 استمتع باستخدام TikTok Scraper!**

**آخر تحديث**: 2025-10-09
**الإصدار**: 1.0.0 (محسّن)
