from aiogram import Router, types, F
from aiogram.filters import Command
from keyboards.video_menu import video_categories_menu, video_list_menu
import logging

router = Router()
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# VIDEO DATABASE - Replace None with actual file_id after uploading
# ═══════════════════════════════════════════════════════════════════
# To get file_id: Send video to bot, it will print file_id in console
VIDEOS = {
    "listening": [
        {
            "title": "📺 Listening Practice 1",
            "file_id": None,  # Replace with actual Telegram file_id
            "description": "Beginner level listening exercises",
            "duration": "5:30"
        },
        {
            "title": "📺 Listening Practice 2", 
            "file_id": None,  # Replace with actual Telegram file_id
            "description": "Intermediate listening practice",
            "duration": "8:15"
        }
    ],
    "pronunciation": [
        {
            "title": "🎤 Pronunciation Guide 1",
            "file_id": None,  # Replace with actual Telegram file_id
            "description": "Basic English pronunciation",
            "duration": "6:45"
        },
        {
            "title": "🎤 Pronunciation Guide 2",
            "file_id": None,  # Replace with actual Telegram file_id
            "description": "Advanced pronunciation",
            "duration": "7:20"
        }
    ],
    "grammar": [
        {
            "title": "✏️ Grammar Lesson 1",
            "file_id": None,  # Replace with actual Telegram file_id
            "description": "Present Simple vs Present Continuous",
            "duration": "10:00"
        },
        {
            "title": "✏️ Grammar Lesson 2",
            "file_id": None,  # Replace with actual Telegram file_id
            "description": "Past tense combinations",
            "duration": "9:30"
        }
    ],
    "vocabulary": [
        {
            "title": "📚 Vocabulary Building 1",
            "file_id": None,  # Replace with actual Telegram file_id
            "description": "Daily life vocabulary",
            "duration": "7:00"
        },
        {
            "title": "📚 Vocabulary Building 2",
            "file_id": None,  # Replace with actual Telegram file_id
            "description": "Business vocabulary",
            "duration": "8:45"
        }
    ]
}

# Admin user ID - set your Telegram user ID to upload videos
ADMIN_USER_ID = 5377298382

@router.message(F.text == "🎥 Videolar")
async def video_menu_handler(message: types.Message):
    """Video kategoriyalarini ko'rsatish"""
    await message.answer(
        "📺 Qaysi turdagi video darslarni ko'rishni xohlaysiz?\n\n"
        "Kategoriyani tanlang:",
        reply_markup=video_categories_menu()
    )


@router.message(F.text == "📻 Tinglash")
async def listening_videos(message: types.Message):
    """Tinglash videolari"""
    await show_videos(message, "listening", "📻 Tinglash Videolari")


@router.message(F.text == "🎤 Talaffuz")
async def pronunciation_videos(message: types.Message):
    """Talaffuz videolari"""
    await show_videos(message, "pronunciation", "🎤 Talaffuz Videolari")


@router.message(F.text == "✏️ Grammatika Videolar")
async def grammar_videos(message: types.Message):
    """Grammatika videolari"""
    await show_videos(message, "grammar", "✏️ Grammatika Videolari")


@router.message(F.text == "📚 So'z Videolar")
async def vocabulary_videos(message: types.Message):
    """Lug'at videolari"""
    await show_videos(message, "vocabulary", "📚 So'z Videolari")


@router.message(F.text == "⬅️ Orqaga")
async def back_to_main(message: types.Message):
    """Asosiy menuga qaytish"""
    from keyboards.menus import main_menu
    await message.answer("🏠 Asosiy menu", reply_markup=main_menu)


async def show_videos(message: types.Message, category: str, title: str):
    """Kategoriya uchun videolarni ko'rsatish"""
    if category not in VIDEOS:
        await message.answer("❌ Bunday kategoriya topilmadi.")
        return
    
    videos = VIDEOS[category]
    text = f"{title}\n\n"
    
    for i, video in enumerate(videos, 1):
        text += f"{i}️⃣ {video['title']}\n   {video['description']}\n\n"
    
    await message.answer(
        text + "⬇️ Video raqamini tanlang yoki \"Orqaga\" ni bosing:",
        reply_markup=video_list_menu(category, len(videos))
    )


@router.message(F.text.contains("📺 Video"))
async def play_video_handler(message: types.Message):
    """Send the selected video to user"""
    text = message.text
    parts = text.split("_")
    
    if len(parts) >= 3:
        category = parts[1]
        try:
            video_num = int(parts[2]) - 1
        except ValueError:
            await message.answer("❌ Invalid video number")
            return
        
        if category in VIDEOS and 0 <= video_num < len(VIDEOS[category]):
            video = VIDEOS[category][video_num]
            
            # Check if video file_id exists
            if video['file_id'] is None:
                await message.answer(
                    f"⚠️ Video not uploaded yet!\n\n"
                    f"📹 {video['title']}\n"
                    f"📝 {video['description']}\n\n"
                    f"Please contact admin to upload this video.",
                    reply_markup=video_categories_menu()
                )
                return
            
            # Send actual video file
            try:
                await message.answer("⏳ Loading video...")
                await message.answer_video(
                    video=video['file_id'],
                    caption=(
                        f"🎬 {video['title']}\n\n"
                        f"📝 {video['description']}\n"
                        f"⏱ Duration: {video.get('duration', 'N/A')}\n\n"
                        f"💡 Tip: After watching, try to practice speaking and check grammar!"
                    ),
                    reply_markup=video_categories_menu()
                )
                logger.info(f"Video sent to user {message.from_user.id}: {video['title']}")
            except Exception as e:
                logger.error(f"Error sending video: {e}")
                await message.answer(
                    f"❌ Error playing video. Please try again later.",
                    reply_markup=video_categories_menu()
                )
        else:
            await message.answer("❌ Video not found", reply_markup=video_categories_menu())


# ═══════════════════════════════════════════════════════════════════
# ADMIN HANDLERS - For uploading videos and getting file_id
# ═══════════════════════════════════════════════════════════════════

@router.message(F.video)
async def handle_video_upload(message: types.Message):
    """Capture uploaded videos and print their file_id"""
    # Only respond to admin (optional - remove check to allow all users)
    if ADMIN_USER_ID and message.from_user.id != ADMIN_USER_ID:
        return
    
    video = message.video
    file_id = video.file_id
    file_size = video.file_size
    duration = video.duration
    
    # Print to console
    logger.info(f"\n{'='*60}")
    logger.info(f"VIDEO UPLOADED by user {message.from_user.id}")
    logger.info(f"File ID: {file_id}")
    logger.info(f"Duration: {duration} seconds")
    logger.info(f"File Size: {file_size / (1024*1024):.2f} MB")
    logger.info(f"{'='*60}\n")
    
    # Send response to user
    await message.answer(
        f"✅ Video received!\n\n"
        f"📹 Duration: {duration}s\n"
        f"💾 Size: {file_size / (1024*1024):.2f} MB\n\n"
        f"🆔 **File ID (copy this):**\n"
        f"`{file_id}`\n\n"
        f"📝 To use this video:\n"
        f"1. Copy the file_id above\n"
        f"2. Open handlers/videos.py\n"
        f"3. Replace 'None' in VIDEOS dictionary\n"
        f"4. Restart the bot",
        parse_mode="Markdown"
    )


@router.message(Command("upload_help"))
async def upload_help_command(message: types.Message):
    """Show instructions for uploading videos"""
    await message.answer(
        "📹 **How to Upload Videos**\n\n"
        "1️⃣ Send any video to this bot\n"
        "2️⃣ Bot will reply with the file_id\n"
        "3️⃣ Copy that file_id\n"
        "4️⃣ Open `bot/handlers/videos.py`\n"
        "5️⃣ Find the VIDEOS dictionary\n"
        "6️⃣ Replace `None` with your file_id\n"
        "7️⃣ Restart the bot\n\n"
        "Example:\n"
        "```python\n"
        '"file_id": "BAACAgIAAxkBAAIBEGX..."\n'
        "```\n\n"
        "✅ Done! Users can now watch that video.",
        parse_mode="Markdown"
    )


def register(dp):
    dp.include_router(router)
