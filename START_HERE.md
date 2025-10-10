# 🚀 ابدأ من هنا - TikTok Scraper

## ✅ تم إصلاح جميع الأخطاء!

النظام يعمل الآن بشكل كامل وجاهز للاستخدام.

---

## 🎯 الوصول السريع

### 1️⃣ الخادم يعمل على:
- **🏠 الصفحة الرئيسية**: http://127.0.0.1:8000
- **📚 توثيق API التفاعلي**: http://127.0.0.1:8000/docs
- **🏥 فحص الصحة**: http://127.0.0.1:8000/health

### 2️⃣ لوحة التحكم (Streamlit):
```bash
streamlit run admin/dashboard.py
```
ثم افتح: http://localhost:8501

---

## 📝 إنشاء أول مهمة

### عبر المتصفح (Swagger UI):

1. افتح: http://127.0.0.1:8000/docs
2. انقر على **POST /api/v1/jobs**
3. انقر على **Try it out**
4. استخدم هذا المثال:

```json
{
  "mode": "profile",
  "value": "khaby.lame",
  "limit": 10,
  "no_watermark": true
}
```

5. انقر على **Execute**

### عبر cURL:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/jobs" ^
  -H "Content-Type: application/json" ^
  -d "{\"mode\":\"profile\",\"value\":\"khaby.lame\",\"limit\":10,\"no_watermark\":true}"
```

### عبر Python:

```python
import requests

response = requests.post("http://127.0.0.1:8000/api/v1/jobs", json={
    "mode": "profile",
    "value": "khaby.lame",
    "limit": 10,
    "no_watermark": True
})

job = response.json()
print(f"Job ID: {job['id']}")
print(f"Status: {job['status']}")
```

---

## 🔍 التحقق من حالة المهمة

### عبر Swagger UI:
1. افتح: http://127.0.0.1:8000/docs
2. انقر على **GET /api/v1/jobs/{job_id}**
3. أدخل Job ID
4. انقر على **Execute**

### عبر cURL:
```bash
curl "http://127.0.0.1:8000/api/v1/jobs/YOUR_JOB_ID"
```

---

## 📊 عرض الإحصائيات

افتح: http://127.0.0.1:8000/api/v1/stats

أو استخدم:
```bash
curl "http://127.0.0.1:8000/api/v1/stats"
```

---

## 🎬 أمثلة الاستخدام

### 1. جلب فيديوهات من ملف شخصي:
```json
{
  "mode": "profile",
  "value": "khaby.lame",
  "limit": 50,
  "no_watermark": true
}
```

### 2. جلب فيديوهات من هاشتاق:
```json
{
  "mode": "hashtag",
  "value": "funny",
  "limit": 30,
  "no_watermark": true
}
```

### 3. جلب فيديوهات بفترة زمنية محددة:
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

---

## 🛠️ الأوامر المفيدة

### تشغيل الخادم:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### تشغيل لوحة التحكم:
```bash
streamlit run admin/dashboard.py
```

### اختبار سريع:
```bash
python test_api_quick.py
```

### تهيئة قاعدة البيانات:
```bash
python scripts/init_db.py
```

### اختبار السكريبر:
```bash
python scripts/test_scraper.py --mode profile --value khaby.lame --limit 5
```

---

## 📂 هيكل المجلدات

```
downloads/              # الفيديوهات المحملة محلياً
├── profile/
│   └── username/
│       └── video_id.mp4
└── hashtag/
    └── tagname/
        └── video_id.mp4

logs/                   # سجلات النظام
├── app_YYYY-MM-DD.log
└── errors_YYYY-MM-DD.log
```

---

## ⚙️ إعداد Google Drive (اختياري)

لرفع الفيديوهات تلقائياً إلى Google Drive:

1. انتقل إلى [Google Cloud Console](https://console.cloud.google.com/)
2. أنشئ مشروع جديد
3. فعّل Google Drive API
4. أنشئ OAuth 2.0 credentials (Desktop app)
5. حمّل الملف إلى `credentials/google_drive_credentials.json`
6. شغّل:
```bash
python scripts/setup_google_drive.py
```

---

## 🐛 حل المشاكل

### الخادم لا يعمل:
```bash
# تحقق من أن المنفذ 8000 غير مستخدم
netstat -ano | findstr :8000

# أو استخدم منفذ آخر
python -m uvicorn app.main:app --port 8001
```

### خطأ في الاستيراد:
```bash
# تثبيت المكتبات المفقودة
pip install -r requirements.txt
```

### خطأ في قاعدة البيانات:
```bash
# إعادة تهيئة قاعدة البيانات
del tiktok_scraper.db
python scripts/init_db.py
```

---

## 📚 التوثيق الكامل

- **README.md** - دليل شامل
- **QUICKSTART.md** - دليل البدء السريع
- **API_DOCUMENTATION.md** - توثيق API كامل
- **DEPLOYMENT.md** - دليل النشر
- **SETUP_CHECKLIST.md** - قائمة التحقق

---

## 🎉 كل شيء جاهز!

النظام يعمل الآن بشكل كامل. يمكنك:

✅ إنشاء مهام جلب الفيديوهات
✅ مراقبة حالة المهام
✅ عرض الفيديوهات المحملة
✅ جدولة مهام دورية
✅ رفع إلى Google Drive (بعد الإعداد)

**استمتع باستخدام TikTok Scraper!** 🚀

---

## 💡 نصائح

1. **ابدأ بعدد قليل من الفيديوهات** (5-10) للاختبار
2. **راقب السجلات** في مجلد `logs/` لمتابعة التقدم
3. **استخدم لوحة التحكم** لواجهة أسهل
4. **احترم حدود المعدل** لتجنب الحظر من TikTok

---

**آخر تحديث**: 2025-10-09
**الإصدار**: 1.0.0
**الحالة**: ✅ يعمل بشكل كامل
