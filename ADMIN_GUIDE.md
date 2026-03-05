# 📚 ADMIN PANEL - VIDEO DARSLAR VA KITOBLAR JOYLASHTIRISH

## Admin Panel Nima?

Django admin panel - video darslar, so'zlar, grammar qoidalari va user management'ni boshqarish uchun built-in web interface.

**URL**: `https://your-domain.com/admin`

---

## Setup: Admin User Yaratish

### Local Development'da:
```bash
cd backend
python manage.py createsuperuser
# Username va password'ni set qilish
```

### Production (Render)'da:
```bash
# Render dashboard → Shell tab
python backend/manage.py createsuperuser
```

---

## Video Darslar Joylashtirish

### 1️⃣ Admin Panel'ga kirgch:
1. `https://your-domain.com/admin` bo'shing
2. **Username** va **Password**'ni kiriting
3. **Videos** bo'limiga o'ting

### 2️⃣ Yangi Video qo'shish:
**Click → "Add Video"**

```
📝 Title: "English Basics for Beginners"
📄 Description: "Bu video'da basic English greetings va introductions o'rganamiz"
🎯 Level: Beginner (dropdown'dan tanlash)
🏷️ Category: General (yoki yangi category yaratish)

🎬 YouTube URL: https://www.youtube.com/watch?v=xxxxxx
🖼️ Thumbnail: Image upload (optional)
⏱️ Duration (seconds): 600  (10 minutes)
👁️ Views: 0 (automatik update bo'ladi)
```

**Save qilish** → Video qo'shildi! ✅

---

## Kitob Joylashtirish

> Kitoblar uchun Word model'idan foydalanishimiz mumkin yoki Document model qo'shish

### Option 1: Word Model'dan foydalanish (simple)
```
Admin Panel → Words → Add Word
- Word: "Chapter 1: Introduction"
- Meaning: "Kitob: English Learning Basics - 1-bob"
- Level: beginner
- Category: Books
```

### Option 2: Alohida Document Model yaratish (advanced)
Backend'ga yangi model qo'shish:

```python
# api/models.py
class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    pdf_file = models.FileField(upload_to='documents/')  # PDF upload
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## Content Management (CRUD)

### ✏️ Tahrir qilish:
1. Admin panel'da **Videos** → Video'ni tanlash
2. **Edit** → O'zgartirishni qilish
3. **Save**

### 🗑️ O'chirish:
1. **Videos** → Checkbox'ni tanlash
2. Action dropdown'dan **Delete**'ni tanlash
3. **Go** → Confirm

### 🔍 Qidirish:
Admin'da Search box' → Video'ni nomi bo'yicha qidirish

### 📊 Filter:
- **Level bo'yicha**: Beginner, Intermediate, IELTS
- **Category bo'yicha**: General, Grammar, Pronunciation, etc.
- **Created Date bo'yicha**: Qachon qo'shilgani

---

## API Orqali Video Qo'shish (Advanced)

```bash
curl -X POST http://localhost:8000/api/videos/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Grammar",
    "description": "Complex grammar structures",
    "level": "intermediate",
    "category": 1,
    "youtube_url": "https://youtube.com/...",
    "duration_seconds": 1200
  }'
```

---

## Bulk Import (Excel'dan videolar qo'shish)

### Step 1: CSV file yaratish
```csv
title,description,level,category,youtube_url,duration_seconds
"English Basics","Beginners course","beginner","General","https://youtube.com/...",600
"Advanced Grammar","Grammar rules","intermediate","Grammar","https://youtube.com/...",1200
```

### Step 2: Python script orqali import qilish
```python
import csv
import django
from api.models import Video, Category

with open('videos.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        category = Category.objects.get(name=row['category'])
        Video.objects.create(
            title=row['title'],
            description=row['description'],
            level=row['level'],
            category=category,
            youtube_url=row['youtube_url'],
            duration_seconds=int(row['duration_seconds'])
        )
```

---

## User Management

### 👥 Foydalanuvchilarni ko'rish:
Admin → Users → Barcha foydalanuvchilarni ko'rish

### 📊 User Statistics:
- **Total Users**
- **Level'ga mos users**
- **Streak bo'yicha reyting**
- **Test natijalar**

---

## Performance Tips

1. **Batch Upload**: Ko'p videolarni bulk qo'shish uchun CSV import'ni ishlatish
2. **Caching**: Video list frequent'ni request qilsangiz cache qilish
3. **Thumbnail Optimization**: Compress qilgan image'lar yuklamath
4. **Database Backups**: Neon'da automatik backup'lar mavjud

---

## Security

⚠️ **Admin credentials'ni save qilish uchun**:
- `.env` file'ga admin username/password'ni keep qilmang
- Hali vaqtda password change qiling
- Django admin'ni production'da IP restriction'iga qo'ying

---

## Troubleshooting

**Q: Admin Panel'ga kirishni bo'lmayapti?**
- Database migration'ni check qilish: `python manage.py migrate`
- Superuser create qilish: `python manage.py createsuperuser`

**Q: Video'lar ko'rinmayotgan bo'lsa?**
- Static files collect qilish: `python manage.py collectstatic`
- Browser cache clear qilish (Ctrl+Shift+Delete)

**Q: Thumbnail upload'i ishlamayotgan bo'lsa?**
- Media folder permissions check qilish
- MEDIA_ROOT va MEDIA_URL settings'ni check qilish (settings.py)

---

✅ **Admin Panel'da har qanday content'ni boshqarishingiz mumkin!**
