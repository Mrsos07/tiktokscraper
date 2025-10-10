# 📤 إعداد Google Drive (اختياري)

## لماذا Google Drive؟

- ✅ مساحة تخزين كبيرة (15GB مجاناً)
- ✅ نسخ احتياطي تلقائي
- ✅ وصول من أي جهاز
- ✅ مشاركة سهلة
- ✅ تنظيم تلقائي بالمجلدات

---

## 📋 خطوات الإعداد

### 1. إنشاء مشروع Google Cloud

1. اذهب إلى: https://console.cloud.google.com/
2. انقر على **Create Project**
3. اسم المشروع: `TikTok Scraper`
4. انقر على **Create**

### 2. تفعيل Google Drive API

1. في القائمة الجانبية، اذهب إلى **APIs & Services** > **Library**
2. ابحث عن: `Google Drive API`
3. انقر على **Enable**

### 3. إنشاء OAuth Credentials

1. اذهب إلى **APIs & Services** > **Credentials**
2. انقر على **+ CREATE CREDENTIALS**
3. اختر **OAuth client ID**
4. Application type: **Desktop app**
5. Name: `TikTok Scraper Desktop`
6. انقر على **Create**

### 4. تحميل ملف Credentials

1. بعد الإنشاء، ستظهر نافذة
2. انقر على **DOWNLOAD JSON**
3. احفظ الملف باسم: `google_drive_credentials.json`

### 5. نقل الملف إلى المشروع

```bash
# أنشئ مجلد credentials إذا لم يكن موجوداً
mkdir credentials

# انقل الملف المحمل
move Downloads\google_drive_credentials.json credentials\
```

### 6. تشغيل سكريبت الإعداد

```bash
python scripts/setup_google_drive.py
```

**سيفتح متصفح:**
1. اختر حساب Google الخاص بك
2. انقر على **Allow**
3. سيتم إنشاء `google_drive_token.json` تلقائياً

### 7. التحقق من الإعداد

```bash
python -c "from app.storage.google_drive import GoogleDriveManager; m = GoogleDriveManager(); m.authenticate(); print('✅ Google Drive ready!')"
```

---

## 🎯 الاستخدام

### بدون تحديد مجلد (افتراضي)

```json
{
  "mode": "profile",
  "value": "username",
  "limit": 10,
  "no_watermark": true
}
```

سيتم الحفظ في:
```
Google Drive/
└── TikTok/
    └── profile/
        └── username/
            └── 2025/
                └── 01/
                    ├── video_id.mp4
                    └── video_id_metadata.json
```

### مع تحديد مجلد معين

1. أنشئ مجلد في Google Drive
2. افتح المجلد واحصل على ID من الرابط:
   ```
   https://drive.google.com/drive/folders/1ABC...XYZ
                                            ↑ هذا هو الـ ID
   ```
3. استخدمه في المهمة:

```json
{
  "mode": "profile",
  "value": "username",
  "limit": 10,
  "drive_folder_id": "1ABC...XYZ",
  "no_watermark": true
}
```

---

## 🔧 إعدادات متقدمة

### في ملف .env:

```env
# ملف الـ credentials
GOOGLE_DRIVE_CREDENTIALS_FILE=./credentials/google_drive_credentials.json

# ملف الـ token (يُنشأ تلقائياً)
GOOGLE_DRIVE_TOKEN_FILE=./credentials/google_drive_token.json

# (اختياري) مجلد جذر افتراضي
GOOGLE_DRIVE_ROOT_FOLDER_ID=1ABC...XYZ
```

---

## ❓ الأسئلة الشائعة

### هل يمكن استخدام حساب Google مجاني؟
✅ نعم، 15GB مجاناً

### هل البيانات آمنة؟
✅ نعم، OAuth2 آمن ولا نحفظ كلمة المرور

### ماذا لو انتهت صلاحية Token؟
✅ سيتم تجديده تلقائياً

### هل يمكن تعطيل Google Drive لاحقاً؟
✅ نعم، فقط احذف ملفات credentials

### هل يمكن استخدام حسابات متعددة؟
✅ نعم، لكن تحتاج credentials منفصلة لكل حساب

---

## 🐛 حل المشاكل

### خطأ: "credentials not found"
```bash
# تأكد من وجود الملف
dir credentials\google_drive_credentials.json
```

### خطأ: "invalid token"
```bash
# احذف Token وأعد المصادقة
del credentials\google_drive_token.json
python scripts\setup_google_drive.py
```

### خطأ: "insufficient permissions"
- تأكد من تفعيل Google Drive API
- أعد إنشاء OAuth credentials

---

## 📊 المراقبة

### التحقق من الرفع:

```python
import requests

response = requests.get("http://127.0.0.1:8000/api/v1/videos")
videos = response.json()['videos']

for video in videos:
    if video['drive_file_id']:
        print(f"✅ {video['id']} - مرفوع")
        print(f"   🔗 https://drive.google.com/file/d/{video['drive_file_id']}/view")
    else:
        print(f"❌ {video['id']} - غير مرفوع")
```

---

## 💡 نصائح

1. **استخدم حساب منفصل** للمشاريع
2. **نظم المجلدات** حسب التاريخ
3. **راقب المساحة** المتبقية
4. **احتفظ بنسخة** من credentials
5. **لا تشارك** ملفات credentials

---

**✅ بعد الإعداد، سيتم رفع جميع الفيديوهات تلقائياً إلى Google Drive!**
