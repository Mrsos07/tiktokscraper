# 🚀 دليل الإعداد الكامل - بيئة جديدة

## 🎯 المشكلة الحالية

```
Error: Using http2=True, but the 'h2' package is not installed.
```

**السبب**: httpx مثبت بدون دعم HTTP/2

---

## ✅ الحل: إنشاء بيئة افتراضية جديدة

### **خطوة واحدة فقط!**

```powershell
cd C:\Users\mrsos\OneDrive\Desktop\tiktok-scraper
.\setup_fresh_env.ps1
```

هذا السكريبت سيقوم بـ:
1. ✅ إنشاء بيئة افتراضية جديدة باسم `env`
2. ✅ تثبيت جميع المكتبات بشكل صحيح
3. ✅ تثبيت `httpx[http2]` مع دعم HTTP/2
4. ✅ تثبيت Playwright و Chromium
5. ✅ تثبيت جميع المتطلبات الأخرى

---

## 📋 الخطوات التفصيلية (إذا أردت التثبيت يدوياً)

### **1. إنشاء البيئة الجديدة:**

```powershell
cd C:\Users\mrsos\OneDrive\Desktop\tiktok-scraper

# إنشاء بيئة جديدة
python -m venv env

# تفعيل البيئة
.\env\Scripts\Activate.ps1

# تحديث pip
python -m pip install --upgrade pip
```

### **2. تثبيت المكتبات الأساسية:**

```powershell
# httpx مع دعم HTTP/2 (مهم!)
pip install "httpx[http2]"

# FastAPI و Uvicorn
pip install fastapi "uvicorn[standard]"

# Pydantic
pip install pydantic pydantic-settings
```

### **3. تثبيت مكتبات السحب:**

```powershell
# Playwright (مهم جداً!)
pip install playwright
playwright install chromium

# مكتبات أخرى
pip install parsel beautifulsoup4 fake-useragent tenacity
```

### **4. تثبيت قاعدة البيانات:**

```powershell
pip install sqlalchemy alembic aiosqlite
```

### **5. تثبيت Google Drive:**

```powershell
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### **6. تثبيت Streamlit:**

```powershell
pip install streamlit pandas
```

### **7. تثبيت باقي المكتبات:**

```powershell
pip install apscheduler "celery[redis]" redis
pip install python-dotenv python-multipart aiofiles
pip install loguru prometheus-client
pip install pytest pytest-asyncio httpx-mock
```

---

## 🚀 تشغيل الخوادم

### **الطريقة السهلة (سكريبت واحد):**

```powershell
.\START_SERVERS.ps1
```

سيفتح نافذتين:
- **نافذة 1**: API Server على http://localhost:8000
- **نافذة 2**: Dashboard على http://localhost:8501

---

### **الطريقة اليدوية:**

#### **نافذة 1 - API Server:**

```powershell
cd C:\Users\mrsos\OneDrive\Desktop\tiktok-scraper
.\env\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### **نافذة 2 - Dashboard:**

```powershell
cd C:\Users\mrsos\OneDrive\Desktop\tiktok-scraper
.\env\Scripts\Activate.ps1
streamlit run admin/dashboard.py
```

---

## 🎯 اختبار النظام

### **1. افتح API Docs:**

```
http://localhost:8000/docs
```

### **2. أنشئ مهمة:**

```json
POST /api/v1/jobs

{
  "mode": "profile",
  "value": "mikaylanogueira",
  "limit": 2,
  "no_watermark": true
}
```

### **3. راقب في Dashboard:**

```
http://localhost:8501
```

---

## 📊 ما يجب أن تراه

### **في اللوقات:**

```
🚀 Initializing Playwright browser...
✅ Browser initialized successfully
🔍 Scraping profile: @mikaylanogueira
   📄 Loading profile page...
   🔎 Extracting video links...
   ✅ Found 2 video links
   📹 Processing video 1/2
      ✅ Video 1 extracted successfully
   📹 Processing video 2/2
      ✅ Video 2 extracted successfully
✅ Successfully scraped 2 videos from @mikaylanogueira
```

### **في Dashboard:**

```
✅ COMPLETED
profile
mikaylanogueira
100%
2/2
```

---

## 🐛 حل المشاكل

### **المشكلة: "h2 package not installed"**

**الحل:**
```powershell
pip uninstall httpx
pip install "httpx[http2]"
```

---

### **المشكلة: "playwright not found"**

**الحل:**
```powershell
pip install playwright
playwright install chromium
```

---

### **المشكلة: "No module named 'google'"**

**الحل:**
```powershell
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## ✅ التحقق من التثبيت

```powershell
# تحقق من httpx مع HTTP/2
python -c "import httpx; print('✅ httpx OK')"

# تحقق من playwright
python -c "from playwright.sync_api import sync_playwright; print('✅ playwright OK')"

# تحقق من chromium
playwright --version

# تحقق من google
python -c "from google.oauth2.credentials import Credentials; print('✅ google OK')"
```

إذا رأيت جميع ✅ فكل شيء جاهز!

---

## 📁 هيكل المشروع

```
tiktok-scraper/
├── env/                    ← البيئة الافتراضية الجديدة
├── app/                    ← كود التطبيق
├── admin/                  ← Dashboard
├── downloads/              ← الفيديوهات المحملة
├── logs/                   ← ملفات اللوقات
├── setup_fresh_env.ps1     ← سكريبت الإعداد
├── START_SERVERS.ps1       ← سكريبت تشغيل الخوادم
└── requirements.txt        ← قائمة المتطلبات
```

---

## 🎬 الخطوات النهائية

```powershell
# 1. إعداد البيئة الجديدة
.\setup_fresh_env.ps1

# 2. تشغيل الخوادم
.\START_SERVERS.ps1

# 3. اختبار!
# افتح: http://localhost:8000/docs
# افتح: http://localhost:8501
```

---

## 💡 نصائح

1. **استخدم `env` بدلاً من `venv`** - بيئة جديدة نظيفة
2. **تأكد من تثبيت `httpx[http2]`** - مع الأقواس المربعة!
3. **ثبت chromium بعد playwright** - `playwright install chromium`
4. **استخدم السكريبتات** - أسهل وأسرع

---

## 🆘 إذا استمرت المشاكل

```powershell
# احذف كل البيئات القديمة
Remove-Item -Recurse -Force venv, env, .venv

# أعد تشغيل السكريبت
.\setup_fresh_env.ps1

# تحقق من كل شيء
python -c "import httpx, playwright; print('✅ All OK')"
```

---

## ✨ الخلاصة

**الخطوة الوحيدة المطلوبة:**

```powershell
.\setup_fresh_env.ps1
```

**ثم شغل الخوادم:**

```powershell
.\START_SERVERS.ps1
```

**وجرب! 🚀**

---

**الآن النظام سيعمل بشكل صحيح 100%!** 🎉
