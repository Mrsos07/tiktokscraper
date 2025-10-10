# 🐍 دليل إصدار Python الصحيح

## ⚠️ مهم جداً!

**Python 3.13 لا يعمل مع Playwright على Windows!**

يجب استخدام **Python 3.12** أو **Python 3.11**

---

## 🔍 الخطوة 1: تحقق من إصدار Python

```powershell
.\check_python.ps1
```

هذا السكريبت سيفحص:
- ✅ Python 3.12 (مثالي)
- ✅ Python 3.11 (جيد)
- ❌ Python 3.13 (لا يعمل!)

---

## 📥 الخطوة 2: تثبيت Python 3.12 (إذا لزم الأمر)

### **تحميل:**
https://www.python.org/downloads/release/python-3120/

### **اختر:**
- Windows installer (64-bit)

### **أثناء التثبيت:**
1. ✅ **Add Python 3.12 to PATH**
2. ✅ **Install for all users**
3. اضغط "Install Now"

---

## 🚀 الخطوة 3: إنشاء البيئة الافتراضية

```powershell
.\setup_fresh_env.ps1
```

هذا السكريبت سيقوم بـ:
1. ✅ البحث عن Python 3.12 أو 3.11 تلقائياً
2. ✅ إنشاء بيئة `env` جديدة
3. ✅ تثبيت جميع المكتبات
4. ✅ تثبيت Playwright و Chromium

**إذا لم يجد Python 3.12/3.11، سيعطيك رسالة خطأ واضحة!**

---

## 🎯 الخطوة 4: تشغيل الخوادم

```powershell
.\START_SERVERS.ps1
```

---

## 📊 مقارنة الإصدارات

| Python | Playwright | asyncio | التوصية |
|--------|-----------|---------|---------|
| 3.13 | ❌ لا يعمل | ❌ مشاكل | لا تستخدم |
| 3.12 | ✅ يعمل | ✅ ممتاز | ⭐ موصى به |
| 3.11 | ✅ يعمل | ✅ ممتاز | ✅ جيد |
| 3.10 | ✅ يعمل | ✅ جيد | ✅ مقبول |

---

## 🔧 استكشاف الأخطاء

### **المشكلة: "Python 3.12 not found"**

**الحل:**
1. ثبت Python 3.12 من الرابط أعلاه
2. أعد تشغيل PowerShell
3. شغل `.\check_python.ps1` للتحقق
4. شغل `.\setup_fresh_env.ps1`

---

### **المشكلة: "py command not found"**

**الحل:**
```powershell
# استخدم المسار الكامل
C:\Python312\python.exe -m venv env
```

---

### **المشكلة: لدي عدة إصدارات من Python**

**الحل:**
السكريبت `setup_fresh_env.ps1` سيختار الإصدار الصحيح تلقائياً!

---

## 📝 الأوامر المفيدة

```powershell
# تحقق من جميع إصدارات Python
.\check_python.ps1

# أنشئ بيئة جديدة (يختار Python 3.12 تلقائياً)
.\setup_fresh_env.ps1

# شغل الخوادم
.\START_SERVERS.ps1

# تحقق من إصدار Python في البيئة الحالية
python --version
```

---

## 🎬 الخطوات الكاملة

```powershell
# 1. تحقق من Python
.\check_python.ps1

# 2. إذا لم يكن لديك Python 3.12، ثبته من:
# https://www.python.org/downloads/release/python-3120/

# 3. أنشئ البيئة (يختار الإصدار الصحيح تلقائياً)
.\setup_fresh_env.ps1

# 4. شغل الخوادم
.\START_SERVERS.ps1

# 5. جرب!
# افتح: http://localhost:8000/docs
```

---

## ✅ التحقق النهائي

بعد إنشاء البيئة:

```powershell
# فعّل البيئة
.\env\Scripts\Activate.ps1

# تحقق من الإصدار
python --version
# يجب: Python 3.12.x أو 3.11.x

# تحقق من Playwright
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright OK')"

# إذا رأيت ✅ Playwright OK، كل شيء جاهز!
```

---

## 🆘 الدعم

إذا واجهت مشاكل:

1. شغل `.\check_python.ps1` وأرسل النتيجة
2. تأكد من تثبيت Python 3.12
3. احذف مجلد `env` وأعد تشغيل `.\setup_fresh_env.ps1`

---

## 💡 ملخص

- ❌ **Python 3.13** → لا يعمل مع Playwright
- ✅ **Python 3.12** → مثالي (موصى به)
- ✅ **Python 3.11** → جيد (بديل)

**السكريبت `setup_fresh_env.ps1` سيختار الإصدار الصحيح تلقائياً!**

---

**الآن شغل `.\check_python.ps1` للبدء! 🚀**
