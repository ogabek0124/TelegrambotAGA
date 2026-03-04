# Deployment Guide - InglizchaOson Bot

## Content Status ✅
- **Vocabulary**: Expanded from 18 → 31 words (10 beginner, 10 intermediate, 11 IELTS)
- **Grammar Topics**: Expanded from 10 → 24 grammar lessons
- **Bot Status**: Fully functional and running

## Deployment Options

### Option 1: GitHub (FREE) ⭐ Recommended for CV
Best for: Portfolio, CV, GitHub contributions, backup

**Steps:**
```bash
# 1. Initialize git repo
git init

# 2. Create .gitignore
echo venv/
echo __pycache__/
echo *.db
echo config.py
> .gitignore

# 3. Add files
git add -A

# 4. First commit
git commit -m "Initial commit: InglizchaOson English Learning Bot"

# 5. Create repo on GitHub (https://github.com/new)

# 6. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/inglizchaoson_bot.git
git branch -M main
git push -u origin main
```

**Benefits:**
✅ Free hosting for code
✅ Portfolio showcase
✅ CV proof of work
✅ Open source option
✅ Version control

---

### Option 2: Cloud Hosting (Bot Keep Running 24/7)

#### A. PythonAnywhere (Easy, Beginner-friendly)
**Cost**: Free tier available ($5/month for paid)

1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Create free account
3. Upload your bot files
4. Set up scheduled task to run bot.py
5. Bot runs 24/7

#### B. Heroku (Popular, but requires credit card)
**Cost**: Free tier removed (now requires payment)

Alternative: Use PythonAnywhere instead

#### C. AWS/Google Cloud (Professional)
**Cost**: Free tier available, then $5-20/month
- More complex setup
- Better for production
- Requires more configuration

#### D. VPS (Virtual Private Server)
**Cost**: $3-5/month (DigitalOcean, Linode)
- Full control
- Reliable
- Easy to scale

---

### Option 3: Local + Database Backup (Hybrid)
Keep running locally, backup data to cloud:

```bash
# Backup database to Google Drive / Dropbox / GitHub
# Run backup script weekly to save data/progress.db
```

---

## Current Setup Status

### Database Location
- **Local**: `data/progress.db` (SQLite)
- **Data Files**: `data/words.json`, `data/grammar.json`

### To Make Persistent:
```python
# In bot.py, add cloud backup:
import shutil
import os
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/progress_{timestamp}.db"
    shutil.copy("data/progress.db", backup_file)
```

---

## Recommended Path for You

1. **Week 1-2**: GitHub push (for portfolio)
   ```bash
   git push to GitHub
   ```

2. **Week 3-4**: PythonAnywhere deployment (24/7 bot)
   - Upload files
   - Configure scheduled task
   - Bot runs continuously

3. **Optional**: Add .env file for TOKEN (keep secure)
   ```bash
   # .gitignore should include:
   .env
   *.db
   ```

---

## Quick Start Commands

### Local Testing
```bash
python bot.py
```

### Push to GitHub
```bash
git add -A
git commit -m "Add expanded vocabulary and grammar"
git push
```

### PythonAnywhere Setup
1. Create account (free)
2. Upload bot files
3. Create web app → scheduled task
4. Set to run: `python /home/username/bot.py`

---

## Summary

✅ **Done**: Expanded content (31 words, 24 grammar topics)
✅ **Ready for**: GitHub portfolio + CV
🔄 **Next Steps**: Push to GitHub, then optionally deploy to PythonAnywhere

**Questions?** See README.md for architecture details.
