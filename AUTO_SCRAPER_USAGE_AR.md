# 🤖 Auto Scraper - المراقبة التلقائية

## 📋 الوصف
النظام يراقب الحسابات تلقائياً ويحمل **الفيديوهات الجديدة فقط**

### كيف يعمل؟
1. يحفظ آخر فيديو للحساب
2. يفحص كل ساعة (أو المدة المحددة)
3. إذا وجد فيديو جديد → يحمله ويرفعه على Google Drive
4. إذا لا يوجد جديد → ينتظر ويفحص مرة أخرى

---

## 🚀 الاستخدام

### 1. إضافة حساب للمراقبة

```bash
POST /api/v1/monitoring/accounts
Content-Type: application/json

{
  "username": "mikaylanogueira"
}
```

**⚡ مهم:** عند إضافة حساب جديد، سيتم تحميل آخر فيديو **فوراً** قبل بدء الجدولة!

### 2. عرض الحسابات المراقبة

```bash
GET /api/v1/monitoring/accounts
```

### 3. إزالة حساب من المراقبة

```bash
DELETE /api/v1/monitoring/accounts/mikaylanogueira
```

### 4. فحص يدوي فوري

```bash
POST /api/v1/monitoring/check-now
```

---

## 📊 مثال عملي

### إضافة حساب:
```json
POST /api/v1/monitoring/accounts

{
  "username": "mikaylanogueira"
}
```

**النتيجة:**
```json
{
  "success": true,
  "message": "Added @mikaylanogueira to monitoring",
  "accounts": ["mikaylanogueira"]
}
```

### ما يحدث بعد ذلك:

#### فوراً بعد الإضافة:
```
✅ Added @mikaylanogueira to monitoring (every 60 min)
📥 Downloading latest video immediately for @mikaylanogueira...
🔍 Checking @mikaylanogueira for new videos...
🎬 FIRST VIDEO: 7558662988408818951
📥 Downloading initial video and uploading to Google Drive...
📝 Created job abc-123-def
✅ Completed! New video downloaded and uploaded
📊 Stats: 1 new videos found in 1 checks
```

#### الفحص الثاني (بعد ساعة):
```
🔍 Checking @mikaylanogueira for new videos...
✅ No new videos (last: 7558662988408818951)
```

#### الفحص الثالث (بعد ساعتين - فيديو جديد):
```
🔍 Checking @mikaylanogueira for new videos...
🆕 NEW VIDEO FOUND: 7559123456789012345
📥 Downloading and uploading to Google Drive...
✅ Completed! New video downloaded and uploaded
📊 Stats: 2 new videos found in 3 checks
```

---

## ⚙️ الإعدادات

### تغيير مدة الفحص (افتراضياً: 60 دقيقة)

في `app/scheduler/auto_scraper.py`:
```python
self.check_interval = 3600  # بالثواني (3600 = ساعة)
```

أو لكل حساب:
```python
await auto_scraper.add_account("username", check_interval_minutes=30)
```

---

## 📂 قاعدة البيانات

### جدول `monitored_accounts`:
| Field | Description |
|-------|-------------|
| `username` | اسم الحساب |
| `last_video_id` | آخر فيديو تم رصده |
| `last_check_at` | آخر وقت فحص |
| `last_new_video_at` | آخر فيديو جديد |
| `enabled` | مفعل أم لا |
| `check_interval_minutes` | مدة الفحص |
| `total_checks` | عدد الفحوصات |
| `total_new_videos` | عدد الفيديوهات الجديدة |

---

## 🎯 المميزات

✅ **ذكي**: يحمل الفيديوهات الجديدة فقط
✅ **تلقائي**: يعمل في الخلفية بدون تدخل
✅ **موفر**: لا يحمل نفس الفيديو مرتين
✅ **سريع**: رفع تلقائي لـ Google Drive
✅ **إحصائيات**: يتتبع عدد الفحوصات والفيديوهات

---

## 🔍 المراقبة

### عرض حالة النظام:
```bash
GET /api/v1/monitoring/status
```

**النتيجة:**
```json
{
  "enabled": true,
  "accounts": ["mikaylanogueira", "username2"],
  "check_interval_minutes": 60
}
```

---

## 💡 نصائح

1. **للحسابات النشطة**: استخدم `check_interval_minutes=30` (كل 30 دقيقة)
2. **للحسابات العادية**: استخدم `check_interval_minutes=60` (كل ساعة)
3. **للحسابات البطيئة**: استخدم `check_interval_minutes=180` (كل 3 ساعات)

---

## 🚨 ملاحظات مهمة

- النظام يبدأ تلقائياً مع الخادم
- الفيديوهات تُرفع تلقائياً إلى Google Drive
- يمكن إضافة عدد غير محدود من الحسابات
- كل حساب له إعداداته الخاصة
