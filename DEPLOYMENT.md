# 🚀 RENDER VA NEON DATABASE'GA DEPLOYMENT

## Step 1: Neon Database o'rnatish

1. **Neon.tech'ga kiring**: https://console.neon.tech/
2. **Yangi project yaratish**: "Create project"
3. **PostgreSQL connection string'ni copy qilish**:
   ```
   postgresql://user:password@host/database_name?sslmode=require
   ```

---

## Step 2: Render'ga deploy qilish

### 2.1 GitHub'ni Render'ga bog'lash
1. **Render.com'ga kiring**: https://render.com/
2. **Yangi Web Service**: Dashboard → New → Web Service
3. **GitHub repository'ni select qilish**: `inglizchaoson_bot`
4. **Deploy settings**:
   - **Name**: `inglizchaoson-bot`
   - **Environment**: Python 3
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     gunicorn core.wsgi
     ```

### 2.2 Environment Variables o'rnatish
Render dashboard'da "Environment" tab'ini oching:

```
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:password@host/database_name?sslmode=require
DEBUG=False
ALLOWED_HOSTS=your-render-domain.onrender.com
DJANGO_SECRET_KEY=your-random-secret-key
```

### 2.3 PostgreSQL Database bog'lash
Django migrations'ni ishga tushirish:

```bash
# Render shell'da:
render-cli run bash
python backend/manage.py migrate
python backend/manage.py createsuperuser  # Admin user yaratish
```

---

## Step 3: Bot Worker'ni Render'da ishga tushirish

Telegrambot 24/7 ishlashi uchun separate worker kerak:

### 3.1 Yangi Background Worker yaratish
1. **Dashboard → New → Background Worker**
2. **Sozlamalar**:
   - **Name**: `telegram-bot-worker`
   - **Repository**: GitHub repo
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     cd bot && python bot.py
     ```
3. **Environment variables'ni same qilib set qilish** (BOT_TOKEN, DATABASE_URL, etc.)

---

## Step 4: Joyistirish (Optional - Webhook uchun)

Agar polling (hozir ishlatilayotgan) o'rniga webhook istasangiz:

1. **Render web service URL'ni olish**: `https://your-app.onrender.com`
2. **bot/bot.py'da webhook mode'ga o'tish**
3. `.env'da**: `BOT_MODE=webhook`

---

## Step 5: Video Darslar va Admin Panel

### Admin Panel Setup (Django)
```bash
python backend/manage.py createsuperuser
# Admin panel: https://your-app.onrender.com/admin
```

### Video darslar qo'shish (API orqali)
1. Django admin'ga kiring
2. **Videos** model'ni create qilish va populate qilish
3. Yoki API endpoint'dan foydalanish:
   ```bash
   POST /api/videos/
   Content-Type: application/json
   
   {
     "title": "English Basics",
     "level": "beginner",
     "url": "https://youtube.com/...",
     "description": "..."
   }
   ```

---

## Debugging & Logs

### Render logs'ni ko'rish:
```bash
# Render dashboard → Logs tab
# Web service logs
# Worker logs (bot)
```

### SSH orqali connect qilish:
```bash
# Render shell'ni ochish
render-cli run bash
```

---

## Database Backup (Neon)

Neon automatik backup qiladi, lekin manual backup uchun:
```bash
# Render shell'da
pg_dump $DATABASE_URL > backup.sql
```

---

## Health Check

Bot muvaffaqiyatli ishlamani tekshirish:
1. Render dashboard'dan worker status'ni ko'rish
2. Telegram bot'ga `/start` yozing
3. Logs'da xatolar borligini tekshirish

---

## Muammo hal qilish

### Bot ishlamayotgan bo'lsa:
1. **Logs'ni tekshirish**: `render-cli logs telegram-bot-worker`
2. **BOT_TOKEN tekshirish**: To'g'ri token ga setlangan
3. **Network issues**: Render firewall settings
4. **Database connection**: DATABASE_URL tekshirish

### Deploy shakli bo'lsa:
1. **Build logs'ni tekshirish**
2. **requirements.txt version clashes**
3. **DJANGO_SECRET_KEY va DEBUG settings**

---

✅ **Hammasi tayyor bo'lgach, bot 24/7 Render'da ishladi!**
