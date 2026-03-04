# 🚀 Quick Start - Video Feature

## ⚡ Fast Setup (5 minutes)

### 1. Set Your Admin ID
```python
# In bot/handlers/videos.py, line ~75
ADMIN_USER_ID = 123456789  # Your Telegram user ID
```

**How to get your ID:** Send `/start` to [@userinfobot](https://t.me/userinfobot)

### 2. Upload First Video

1. Open your bot in Telegram
2. Send any video file (MP4, MOV, etc.)
3. Bot replies with something like:

```
✅ Video received!

🎬 Duration: 180s
💾 Size: 15.23 MB

🆔 File ID (copy this):
BAACAgIAAxkBAAIBEGX1234567890abcdefghijk...

📝 To use this video:
1. Copy the file_id above
2. Open handlers/videos.py
3. Replace 'None' in VIDEOS dictionary
4. Restart the bot
```

### 3. Add File ID to Code

Open `bot/handlers/videos.py` and find:

```python
"listening": [
    {
        "title": "📺 Listening Practice 1",
        "file_id": None,  # ← Replace this
        "description": "Beginner level listening exercises",
        "duration": "5:30"
    }
]
```

Change to:

```python
"listening": [
    {
        "title": "📺 Listening Practice 1",
        "file_id": "BAACAgIAAxkBAAIBEGX1234567890abcdefghijk...",  # ← Paste here
        "description": "Beginner level listening exercises",
        "duration": "5:30"
    }
]
```

### 4. Restart Bot

```bash
# Stop current bot (Ctrl+C)
python bot.py
```

### 5. Test It! ✅

In Telegram:
1. Click **🎥 Videolar**
2. Click **📻 Tinglash**
3. Click **📺 Video_listening_1**
4. Bot sends your video! 🎉

---

## 📋 Button Flow

```
🎥 Videolar (Main Menu)
    ↓
📻 Tinglash | 🎤 Talaffuz | ✏️ Grammatika | 📚 So'z
    ↓
📺 Video_listening_1
📺 Video_listening_2
⬅️ Orqaga
    ↓
[Bot sends video file]
```

---

## 🎯 Example: Complete Listening Category

```python
"listening": [
    {
        "title": "📺 Listening Practice 1",
        "file_id": "BAACAgIAAxkBAAIBE...",  # Real file_id here
        "description": "Beginner level listening exercises",
        "duration": "5:30"
    },
    {
        "title": "📺 Listening Practice 2", 
        "file_id": "BAACAgIAAxkBAAIBF...",  # Real file_id here
        "description": "Intermediate listening practice",
        "duration": "8:15"
    }
]
```

---

## ❓ Troubleshooting

**Q: Bot says "Video not uploaded yet"?**
- A: file_id is still `None`, need to upload video and get file_id

**Q: How do I know my video uploaded correctly?**  
- A: Check console logs, should see: `INFO:root:VIDEO UPLOADED by user...`

**Q: Can users upload videos?**
- A: Only if you set `ADMIN_USER_ID = None`. Otherwise only admin can.

**Q: Video file too large?**
- A: Telegram bot limit is 50MB. Compress video using online tools.

---

## 📝 Tips

✅ **DO:**
- Test with 1 video first
- Use descriptive titles
- Keep videos under 50MB
- Update duration field for better UX

❌ **DON'T:**
- Forget to replace 'None' with file_id
- Use same file_id for multiple videos
- Forget to restart bot after changes

---

## 🎨 Customization Examples

### Change Button Text
In `keyboards/video_menu.py`:
```python
[KeyboardButton(text="📻 Listen"), KeyboardButton(text="🎤 Speak")]
```

### Add More Videos
Just add to the list:
```python
"listening": [
    # ... existing videos ...
    {
        "title": "📺 Listening Practice 3",
        "file_id": None,
        "description": "Advanced listening",
        "duration": "12:00"
    }
]
```

### Change Video Caption
In `handlers/videos.py`, find `await message.answer_video()` and edit the `caption` parameter.

---

## 📚 Full Documentation

See [VIDEO_SETUP_GUIDE.md](VIDEO_SETUP_GUIDE.md) for complete documentation.

---

**Ready? Start uploading videos now! 🚀**
