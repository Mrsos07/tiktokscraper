# 🔍 استخدام Explore (صفحة الاستكشاف)

## 📋 الوصف
يمكنك الآن تحميل الفيديوهات من صفحة Explore في TikTok، مثل:
- الجمال والعناية (Beauty)
- الموضة (Fashion)
- الطعام (Food)
- وغيرها...

---

## 🚀 الاستخدام

### 1. عبر API

```bash
POST /api/v1/jobs
Content-Type: application/json

{
  "mode": "explore",
  "value": "beauty",
  "limit": 5,
  "no_watermark": true
}
```

### 2. عبر Dashboard

1. اذهب إلى: http://localhost:8501
2. اختر Mode: **explore**
3. في Value، اكتب اسم التصنيف:
   - `beauty` للجمال والعناية
   - `fashion` للموضة
   - `food` للطعام
4. اختر عدد الفيديوهات
5. انقر "Start Job"

---

## 📂 التصنيفات المتاحة

| العربي | English | Value |
|--------|---------|-------|
| الجمال والعناية | Beauty & Care | `beauty` |
| الموضة | Fashion | `fashion` |
| الطعام | Food | `food` |
| الرياضة | Sports | `sports` |
| الألعاب | Gaming | `gaming` |
| الموسيقى | Music | `music` |

---

## 💾 مكان الحفظ

الفيديوهات تُحفظ في:
```
downloads/explore/beauty/
downloads/explore/fashion/
```

---

## 🧪 اختبار سريع

```powershell
python test_explore.py
```

---

## ⚙️ كيف يعمل؟

1. **Selenium** يفتح صفحة https://www.tiktok.com/explore
2. يبحث عن زر التصنيف (مثل "الجمال والعناية")
3. ينقر عليه
4. يسكرول لتحميل المزيد من الفيديوهات
5. يستخرج روابط الفيديوهات
6. يحمل كل فيديو باستخدام **yt-dlp**
7. يرفعها تلقائياً إلى **Google Drive**

---

## ✅ المميزات

- ✅ يعمل مع جميع التصنيفات
- ✅ بدون علامة مائية
- ✅ رفع تلقائي لـ Google Drive
- ✅ ترجمة عربية (إذا كان ffmpeg مثبت)

---

## 🎯 مثال كامل

```json
{
  "mode": "explore",
  "value": "beauty",
  "limit": 10,
  "no_watermark": true
}
```

**النتيجة:**
- 10 فيديوهات من تصنيف الجمال
- محفوظة في `downloads/explore/beauty/`
- مرفوعة على Google Drive
- مع ترجمة عربية (إذا متوفرة)
