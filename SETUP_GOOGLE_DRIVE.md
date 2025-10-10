# 🔧 إعداد Google Drive API

## الخطوة 1: إنشاء مشروع في Google Cloud

1. اذهب إلى: https://console.cloud.google.com/
2. انقر على "Create Project" أو "إنشاء مشروع"
3. اختر اسم للمشروع (مثل: TikTok-Scraper)
4. انقر "Create"

## الخطوة 2: تفعيل Google Drive API

1. في القائمة الجانبية، اذهب إلى "APIs & Services" > "Library"
2. ابحث عن "Google Drive API"
3. انقر عليه ثم "Enable"

## الخطوة 3: إنشاء OAuth 2.0 Credentials

1. اذهب إلى "APIs & Services" > "Credentials"
2. انقر "Create Credentials" > "OAuth client ID"
3. اختر "Desktop app"
4. اختر اسم (مثل: TikTok Scraper Desktop)
5. انقر "Create"
6. **مهم**: احفظ ملف `credentials.json`

## الخطوة 4: نسخ ملف Credentials

1. انسخ ملف `credentials.json` الذي حملته
2. ضعه في مجلد المشروع:
   ```
   C:\Users\mrsos\OneDrive\Desktop\tiktok-scraper\credentials.json
   ```

## الخطوة 5: تشغيل السكريبت للمصادقة

سيتم إنشاء سكريبت تلقائي للمصادقة...
