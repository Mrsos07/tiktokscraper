# ⚠️ يجب تثبيت Playwright الآن!

## 🔴 المشكلة

الخطأ في اللوقات يقول:
```
❌ Error initializing browser: 
💡 Make sure Playwright is installed: playwright install chromium
```

**السبب**: متصفح Chromium غير مثبت!

---

## ✅ الحل السريع (3 أوامر فقط!)

### **الطريقة 1: استخدام السكريبت التلقائي**

```powershell
cd C:\Users\mrsos\OneDrive\Desktop\tiktok-scraper
.\install_playwright.ps1
```

---

### **الطريقة 2: التثبيت اليدوي**

```powershell
# 1. تفعيل البيئة الافتراضية
cd C:\Users\mrsos\OneDrive\Desktop\tiktok-scraper
.\venv\Scripts\Activate.ps1

# 2. تثبيت/تحديث playwright
pip install --upgrade playwright

# 3. تثبيت متصفح chromium (مهم جداً!)
playwright install chromium
```

---

## 🎯 التحقق من التثبيت

```powershell
# اختبار playwright
python -c "from playwright.sync_api import sync_playwright; print('✅ OK')"

# اختبار chromium
playwright --version
```

**إذا رأيت** `✅ OK` **فالتثبيت نجح!**

---

## 🚀 بعد التثبيت

### **1. أعد تشغيل الخادم:**

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **2. جرب مهمة جديدة:**

```json
POST http://localhost:8000/api/v1/jobs

{
  "mode": "profile",
  "value": "mikaylanogueira",
  "limit": 2,
  "no_watermark": true
}
```

### **3. راقب اللوقات:**

يجب أن ترى:
```
🚀 Initializing Playwright browser...
✅ Browser initialized successfully
🔍 Scraping profile: @mikaylanogueira
   📄 Loading profile page...
   🔎 Extracting video links...
   ✅ Found 2 video links
```

---

## 🐛 إذا استمرت المشكلة

### **الخطأ: "Executable doesn't exist"**

```powershell
# جرب التثبيت بطريقة مختلفة
python -m playwright install chromium

# أو ثبت جميع المتصفحات
python -m playwright install
```

---

### **الخطأ: "Permission denied"**

```powershell
# شغل PowerShell كمسؤول (Run as Administrator)
# ثم نفذ:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
playwright install chromium
```

---

### **الخطأ: "playwright command not found"**

```powershell
# تأكد من تفعيل venv
.\venv\Scripts\Activate.ps1

# أعد تثبيت playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

---

## 📊 ماذا يحدث بدون Playwright؟

بدون Playwright، النظام يحاول:
1. ❌ ReliableScraper (يفشل - يحتاج chromium)
2. ❌ HTTP Scraping (يفشل - TikTok يحمي الصفحات)
3. ❌ Enhanced Scraper (يفشل - يحتاج playwright)

**النتيجة**: "No videos found" ❌

---

## ✅ مع Playwright

مع Playwright مثبت بشكل صحيح:
1. ✅ ReliableScraper (ينجح!)
2. ✅ يستخرج الفيديوهات
3. ✅ يحمل بدون علامة مائية

**النتيجة**: نجاح 95%+ ✅

---

## 🎬 اختبار سريع بعد التثبيت

```powershell
# اختبار من Python مباشرة
python -c "
import asyncio
from app.scrapers.reliable_scraper import ReliableTikTokScraper

async def test():
    async with ReliableTikTokScraper() as scraper:
        print('✅ ReliableScraper works!')

asyncio.run(test())
"
```

إذا رأيت `✅ ReliableScraper works!` فكل شيء جاهز!

---

## 📝 ملخص الخطوات

```powershell
# 1. ثبت chromium
playwright install chromium

# 2. تحقق
playwright --version

# 3. أعد تشغيل الخادم
python -m uvicorn app.main:app --reload

# 4. جرب!
```

---

## 🆘 الدعم

إذا واجهت مشاكل:

```powershell
# افحص اللوقات
Get-Content logs\app_2025-10-09.log -Tail 50 | Select-String "Playwright"

# تحقق من مسار chromium
playwright --version

# أعد التثبيت
pip uninstall playwright
pip install playwright
playwright install chromium
```

---

## ⚡ الآن ثبت Playwright!

```powershell
playwright install chromium
```

**هذا كل ما تحتاجه! 🚀**
