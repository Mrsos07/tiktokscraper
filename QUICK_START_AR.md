# 🚀 دليل البدء السريع

## ✅ تم إصلاح المشكلة!

**المشكلة**: خطأ في معامل `proxies` في httpx
**الحل**: تم تصحيحه إلى `proxy` ✅

---

## 📋 خطوات التشغيل

### 1️⃣ تفعيل البيئة الافتراضية
```bash
cd C:\Users\mrsos\OneDrive\Desktop\tiktok-scraper
.\venv\Scripts\Activate.ps1
```

إذا واجهت خطأ في التفعيل، جرب:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2️⃣ تشغيل الخادم
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3️⃣ فتح واجهة API
افتح المتصفح على: **http://localhost:8000/docs**

---

## 🎯 كيفية إنشاء مهمة سحب

### **الطريقة 1: من واجهة Swagger UI**

1. اذهب إلى: http://localhost:8000/docs
2. اضغط على **POST /api/v1/jobs**
3. اضغط **Try it out**
4. أدخل البيانات:

```json
{
  "mode": "profile",
  "value": "mikaylanogueira",
  "limit": 10,
  "no_watermark": true
}
```

5. اضغط **Execute**

### **الطريقة 2: من PowerShell/CMD**

```powershell
curl -X POST "http://localhost:8000/api/v1/jobs" `
  -H "Content-Type: application/json" `
  -d '{
    "mode": "profile",
    "value": "mikaylanogueira",
    "limit": 10,
    "no_watermark": true
  }'
```

### **الطريقة 3: من Python**

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/jobs",
    json={
        "mode": "profile",
        "value": "mikaylanogueira",
        "limit": 10,
        "no_watermark": True
    }
)

job = response.json()
print(f"Job ID: {job['id']}")
```

---

## 📊 التحقق من حالة المهمة

### **من المتصفح**
```
http://localhost:8000/api/v1/jobs/{job_id}
```

### **من PowerShell**
```powershell
curl "http://localhost:8000/api/v1/jobs/{job_id}"
```

---

## 📁 مكان حفظ الفيديوهات

الفيديوهات تُحفظ في:
```
C:\Users\mrsos\OneDrive\Desktop\tiktok-scraper\downloads\profile\mikaylanogueira\
```

الهيكل:
```
downloads/
├── profile/
│   └── {username}/
│       ├── {video_id_1}.mp4
│       ├── {video_id_2}.mp4
│       └── ...
└── hashtag/
    └── {tag}/
        ├── {video_id_1}.mp4
        └── ...
```

---

## 🔍 أمثلة عملية

### **مثال 1: سحب 5 فيديوهات من بروفايل**
```json
{
  "mode": "profile",
  "value": "charlidamelio",
  "limit": 5,
  "no_watermark": true
}
```

### **مثال 2: سحب 10 فيديوهات من هاشتاق**
```json
{
  "mode": "hashtag",
  "value": "fyp",
  "limit": 10,
  "no_watermark": true
}
```

### **مثال 3: سحب فيديوهات بفلتر تاريخ**
```json
{
  "mode": "profile",
  "value": "username",
  "limit": 15,
  "no_watermark": true,
  "since": "2025-01-01T00:00:00Z",
  "until": "2025-10-09T23:59:59Z"
}
```

---

## 📈 مراقبة التقدم

### **الحالات الممكنة:**
- ✅ **COMPLETED** - اكتملت بنجاح
- ⏳ **RUNNING** - قيد التنفيذ
- ⏸️ **PENDING** - في الانتظار
- ❌ **FAILED** - فشلت

### **عرض جميع المهام:**
```
GET http://localhost:8000/api/v1/jobs
```

### **عرض الإحصائيات:**
```
GET http://localhost:8000/api/v1/stats/system
```

---

## 🐛 حل المشاكل الشائعة

### **المشكلة: "AsyncClient got unexpected keyword argument 'proxies'"**
✅ **تم الحل!** - تم تصحيح الكود

### **المشكلة: لا يمكن تفعيل venv**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **المشكلة: "No videos found"**
- تأكد من صحة اسم المستخدم
- جرب username آخر معروف (مثل: charlidamelio)
- تحقق من اتصال الإنترنت

### **المشكلة: "Download failed"**
- تحقق من مساحة القرص
- تأكد من صلاحيات الكتابة في مجلد downloads
- جرب تقليل عدد الفيديوهات

### **المشكلة: الخادم لا يعمل**
```bash
# تحقق من أن المنفذ 8000 غير مستخدم
netstat -ano | findstr :8000

# إذا كان مستخدماً، أوقف العملية أو استخدم منفذ آخر
python -m uvicorn app.main:app --reload --port 8001
```

---

## 📝 ملاحظات مهمة

### **الحدود:**
- ✅ عدد الفيديوهات: **1-20** (تم تعديله)
- ⏱️ التأخير بين الطلبات: 2-5 ثواني
- 🔄 إعادة المحاولة: 3 مرات تلقائياً

### **الميزات:**
- ✅ تحميل بدون علامة مائية (no watermark)
- ✅ حفظ محلي تلقائي
- ✅ رفع إلى Google Drive (اختياري)
- ✅ معالجة متعددة للمهام
- ✅ تسجيل تفصيلي للأخطاء

---

## 🎬 فيديو توضيحي (خطوات)

1. **شغل الخادم**: `python -m uvicorn app.main:app --reload`
2. **افتح المتصفح**: http://localhost:8000/docs
3. **اضغط POST /api/v1/jobs**
4. **اضغط Try it out**
5. **أدخل البيانات** (mode: profile, value: username, limit: 10)
6. **اضغط Execute**
7. **انسخ job_id من الرد**
8. **افتح GET /api/v1/jobs/{job_id}** للمتابعة
9. **الفيديوهات ستكون في مجلد downloads**

---

## 🆘 الدعم

إذا واجهت أي مشكلة:
1. راجع ملف اللوقات: `logs/app_2025-10-09.log`
2. تحقق من قاعدة البيانات: `tiktok_scraper.db`
3. جرب مع username معروف: `charlidamelio` أو `khaby.lame`

---

## ✨ الآن جرب!

```bash
# 1. شغل الخادم
python -m uvicorn app.main:app --reload

# 2. في نافذة أخرى، أنشئ مهمة
curl -X POST "http://localhost:8000/api/v1/jobs" ^
  -H "Content-Type: application/json" ^
  -d "{\"mode\": \"profile\", \"value\": \"charlidamelio\", \"limit\": 3}"
```

**النظام جاهز للعمل! 🚀**
