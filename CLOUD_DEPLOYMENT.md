# Cloud Deployment Guide - TikTok Scraper

## خيارات النشر المتاحة

### 1. Railway.app (موصى به) ⭐

**المميزات:**
- نشر مجاني حتى 5$ شهرياً
- دعم Docker كامل
- قاعدة بيانات PostgreSQL مجانية
- سهل الاستخدام

**خطوات النشر:**

```bash
# 1. تثبيت Railway CLI
npm install -g @railway/cli

# 2. تسجيل الدخول
railway login

# 3. إنشاء مشروع جديد
railway init

# 4. ربط GitHub repo (اختياري)
railway link

# 5. إضافة PostgreSQL
railway add postgresql

# 6. رفع المتغيرات
railway variables set GOOGLE_DRIVE_CREDENTIALS_FILE=/app/credentials/credentials.json

# 7. نشر التطبيق
railway up

# 8. فتح التطبيق
railway open
```

**الرابط:** https://railway.app

---

### 2. Render.com

**المميزات:**
- خطة مجانية متاحة
- دعم Docker
- قاعدة بيانات PostgreSQL مجانية
- SSL تلقائي

**خطوات النشر:**

1. إنشاء حساب على https://render.com
2. New > Blueprint
3. ربط GitHub repository
4. Render سيكتشف ملف `render.yaml` تلقائياً
5. إضافة environment variables:
   - `GOOGLE_DRIVE_CREDENTIALS_FILE`
   - `GOOGLE_DRIVE_TOKEN_FILE`
6. Deploy

**ملاحظة:** الخطة المجانية تتوقف بعد 15 دقيقة من عدم النشاط

---

### 3. Fly.io

**المميزات:**
- خطة مجانية جيدة
- دعم Docker ممتاز
- سيرفرات عالمية
- دعم volumes للتخزين

**خطوات النشر:**

```bash
# 1. تثبيت Fly CLI
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# 2. تسجيل الدخول
fly auth login

# 3. إنشاء التطبيق
fly launch

# 4. إنشاء volume للتخزين
fly volumes create tiktok_data --size 10

# 5. إضافة secrets
fly secrets set GOOGLE_DRIVE_CREDENTIALS_FILE=/app/credentials/credentials.json

# 6. نشر
fly deploy

# 7. فتح التطبيق
fly open
```

**الرابط:** https://fly.io

---

### 4. DigitalOcean App Platform

**المميزات:**
- سهل الاستخدام
- دعم Docker
- قاعدة بيانات managed
- $5/شهر للخطة الأساسية

**خطوات النشر:**

1. إنشاء حساب على https://www.digitalocean.com
2. Apps > Create App
3. ربط GitHub repository
4. اختيار Dockerfile
5. إضافة environment variables
6. Deploy

---

### 5. Heroku

**المميزات:**
- سهل جداً
- دعم Procfile
- إضافات كثيرة

**خطوات النشر:**

```bash
# 1. تثبيت Heroku CLI
# من: https://devcenter.heroku.com/articles/heroku-cli

# 2. تسجيل الدخول
heroku login

# 3. إنشاء تطبيق
heroku create tiktok-scraper-app

# 4. إضافة buildpack
heroku buildpacks:set heroku/python

# 5. إضافة PostgreSQL
heroku addons:create heroku-postgresql:mini

# 6. إضافة متغيرات
heroku config:set GOOGLE_DRIVE_CREDENTIALS_FILE=/app/credentials/credentials.json

# 7. نشر
git push heroku main

# 8. فتح التطبيق
heroku open
```

**ملاحظة:** Heroku ألغى الخطة المجانية

---

## إعداد Google Drive Credentials

### الطريقة الآمنة:

```bash
# 1. تحويل credentials.json إلى base64
$credentials = Get-Content credentials.json -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($credentials)
$base64 = [Convert]::ToBase64String($bytes)
Write-Output $base64

# 2. إضافة كمتغير بيئي
# Railway:
railway variables set GOOGLE_DRIVE_CREDENTIALS_BASE64="<base64_string>"

# Fly.io:
fly secrets set GOOGLE_DRIVE_CREDENTIALS_BASE64="<base64_string>"

# Render:
# أضف في Dashboard > Environment
```

### في الكود (app/core/config.py):

```python
import base64
import json
from pathlib import Path

# Decode credentials from environment
if os.getenv('GOOGLE_DRIVE_CREDENTIALS_BASE64'):
    credentials_base64 = os.getenv('GOOGLE_DRIVE_CREDENTIALS_BASE64')
    credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
    
    # Save to file
    credentials_path = Path('credentials/credentials.json')
    credentials_path.parent.mkdir(exist_ok=True)
    credentials_path.write_text(credentials_json)
```

---

## المتغيرات البيئية المطلوبة

```bash
# أساسية
DATABASE_URL=postgresql://user:pass@host:5432/dbname
GOOGLE_DRIVE_CREDENTIALS_BASE64=<base64_encoded_json>
GOOGLE_DRIVE_FOLDER_ID=<your_folder_id>

# اختيارية
DEBUG=false
LOG_LEVEL=INFO
MAX_CONCURRENT_DOWNLOADS=3
```

---

## التوصيات

### للاستخدام الشخصي:
✅ **Railway.app** - سهل ومجاني

### للإنتاج:
✅ **Fly.io** - أداء ممتاز
✅ **DigitalOcean** - استقرار عالي

### للتطوير:
✅ **Render.com** - نشر سريع

---

## ملاحظات مهمة

1. **التخزين:**
   - استخدم Object Storage (S3, Spaces) للفيديوهات
   - لا تخزن الفيديوهات على السيرفر

2. **قاعدة البيانات:**
   - استخدم PostgreSQL للإنتاج
   - SQLite للتطوير فقط

3. **الأمان:**
   - لا ترفع credentials.json على Git
   - استخدم environment variables
   - فعّل HTTPS

4. **الأداء:**
   - استخدم Redis للـ caching
   - فعّل CDN للملفات الثابتة

---

## استكشاف الأخطاء

### مشكلة: Playwright لا يعمل
```dockerfile
# في Dockerfile، أضف:
RUN playwright install-deps
```

### مشكلة: ffmpeg غير موجود
```dockerfile
# في Dockerfile، أضف:
RUN apt-get update && apt-get install -y ffmpeg
```

### مشكلة: نفاد المساحة
```bash
# استخدم Google Drive فقط، لا تخزن محلياً
# أو استخدم Object Storage
```

---

## الدعم

للمساعدة في النشر:
1. تحقق من logs السيرفر
2. راجع documentation المنصة
3. تأكد من environment variables

---

## الخلاصة

**الخيار الأفضل:** Railway.app
- سهل الاستخدام
- مجاني للبداية
- دعم Docker كامل
- قاعدة بيانات مدمجة

**الأمر:**
```bash
railway login
railway init
railway up
```

✅ جاهز للنشر!
