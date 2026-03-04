# 📺 Video Lessons Setup Guide

## Overview
This guide explains how to add video lessons to your Telegram bot.

## 🎯 How It Works

1. **User clicks "🎥 Videolar"** → Shows categories (Listening, Pronunciation, Grammar, Vocabulary)
2. **User selects category** → Shows list of videos in that category
3. **User clicks video button** → Bot sends the actual video with description
4. **User clicks "⬅️ Orqaga"** → Returns to previous menu

## 📤 How to Upload Videos

### Step 1: Get Your Telegram User ID
1. Send `/start` to [@userinfobot](https://t.me/userinfobot)
2. Copy your User ID (example: 123456789)
3. Open `bot/handlers/videos.py`
4. Find line: `ADMIN_USER_ID = None`
5. Replace with: `ADMIN_USER_ID = 123456789`

### Step 2: Upload a Video
1. Open your bot in Telegram
2. Simply send any video file to the bot
3. Bot will reply with the **file_id** - something like:
   ```
   File ID: BAACAgIAAxkBAAIBEGX1234567890abcdefghijk...
   ```
4. **Copy this file_id**

### Step 3: Add Video to Bot
1. Open `bot/handlers/videos.py`
2. Find the `VIDEOS` dictionary
3. Locate the video you want to replace (where `file_id: None`)
4. Replace `None` with the copied file_id

**Example:**
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

### Step 4: Restart Bot
1. Stop the current bot (Ctrl+C in terminal)
2. Run: `python bot.py`
3. Done! Video is now available to users

## 📋 Video Categories Structure

```python
VIDEOS = {
    "listening": [...],      # 📻 Tinglash
    "pronunciation": [...],  # 🎤 Talaffuz
    "grammar": [...],        # ✏️ Grammatika Videolar
    "vocabulary": [...]      # 📚 So'z Videolar
}
```

## ➕ Adding New Videos

### To add a new video to existing category:

1. Open `bot/handlers/videos.py`
2. Find your category (e.g., `"listening"`)
3. Add new entry:

```python
"listening": [
    # ... existing videos ...
    {
        "title": "📺 Listening Practice 3",
        "file_id": None,  # Upload video to get file_id
        "description": "Advanced listening comprehension",
        "duration": "12:00"
    }
]
```

4. Upload video to bot to get file_id
5. Replace `None` with the file_id
6. **Important:** Update `keyboards/video_menu.py` if needed

### To create a new category:

1. Add new category to `VIDEOS` dictionary:
```python
VIDEOS = {
    # ... existing categories ...
    "speaking": [
        {
            "title": "🗣 Speaking Practice 1",
            "file_id": None,
            "description": "Basic conversation practice",
            "duration": "8:00"
        }
    ]
}
```

2. Add handler in `videos.py`:
```python
@router.message(F.text == "🗣 Speaking")
async def speaking_videos(message: types.Message):
    """Speaking practice videos"""
    await show_videos(message, "speaking", "🗣 Speaking Practice")
```

3. Add button in `keyboards/video_menu.py`:
```python
def video_categories_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📻 Tinglash"), KeyboardButton(text="🎤 Talaffuz")],
            [KeyboardButton(text="✏️ Grammatika Videolar"), KeyboardButton(text="📚 So'z Videolar")],
            [KeyboardButton(text="🗣 Speaking"), KeyboardButton(text="⬅️ Orqaga")],  # ← New button
        ],
        resize_keyboard=True
    )
```

## 🔧 Troubleshooting

### Video not showing?
- ✅ Check file_id is correctly pasted (no extra spaces)
- ✅ Make sure you restarted the bot after changes
- ✅ Verify video file isn't corrupted

### Bot says "Video not uploaded yet"?
- ✅ file_id is still `None` - need to upload video
- ✅ Check spelling of file_id

### Can't upload video?
- ✅ Set your ADMIN_USER_ID in videos.py
- ✅ Make sure video file size < 50MB (Telegram bot limit)
- ✅ Try compressing video if too large

### Wrong video plays?
- ✅ Check VIDEOS list order matches button order
- ✅ Array indexing starts at 0 (first video = index 0)

## 📝 Video Naming Convention

Follow this pattern for consistency:
- **Listening:** "📺 Listening Practice [number]"
- **Pronunciation:** "🎤 Pronunciation Guide [number]"
- **Grammar:** "✏️ Grammar Lesson [number]"
- **Vocabulary:** "📚 Vocabulary Building [number]"

## 🔐 Security Notes

- Only set ADMIN_USER_ID if you want to restrict video uploads
- If `ADMIN_USER_ID = None`, anyone can send videos to bot (for testing)
- File IDs are unique to your bot and can't be used by other bots

## 🎨 Customization

### Change video captions:
Edit the `caption` parameter in `play_video_handler()`:
```python
caption=(
    f"🎬 {video['title']}\n\n"
    f"📝 {video['description']}\n"
    f"⏱ Duration: {video.get('duration', 'N/A')}\n\n"
    f"💡 Your custom message here!"
)
```

### Add video thumbnails:
```python
await message.answer_video(
    video=video['file_id'],
    caption="...",
    thumb=video.get('thumbnail_file_id')  # Add thumbnail support
)
```

## 📞 Support Commands

Users can use these commands:
- `/upload_help` - Shows upload instructions

## 🚀 Quick Start Checklist

- [ ] Set your ADMIN_USER_ID in videos.py
- [ ] Send test video to bot
- [ ] Copy file_id from bot's response
- [ ] Paste file_id into VIDEOS dictionary
- [ ] Restart bot
- [ ] Test by clicking video button in Telegram
- [ ] Repeat for all videos

---

**Need help?** Check the logs in console for detailed error messages!
