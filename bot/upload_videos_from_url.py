"""
Video URL dan Telegram ga yuklash va file_id olish scripti
"""
import asyncio
import aiohttp
import os
from aiogram import Bot
from config import TOKEN

# Video URL lar
VIDEOS_TO_UPLOAD = {
    "listening_1": "https://yourbotvideos.com/listening/video_listening_1.mp4",
    "listening_2": "https://yourbotvideos.com/listening/video_listening_2.mp4",
}

async def download_video(url: str, filename: str):
    """URL dan video yuklab olish"""
    print(f"📥 Yuklab olinmoqda: {filename}...")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(filename, 'wb') as f:
                    f.write(await response.read())
                print(f"✅ Yuklandi: {filename}")
                return True
            else:
                print(f"❌ Xato: {response.status}")
                return False

async def upload_to_telegram(bot: Bot, filepath: str, title: str):
    """Video ni Telegram ga yuklash va file_id olish"""
    print(f"📤 Telegram ga yuklanmoqda: {title}...")
    
    # Admin user ID ga yuborish
    ADMIN_ID = 5377298382
    
    with open(filepath, 'rb') as video_file:
        message = await bot.send_video(
            chat_id=ADMIN_ID,
            video=video_file,
            caption=f"🎬 {title}\n\n📋 File ID quyida:"
        )
        
        file_id = message.video.file_id
        print(f"✅ File ID: {file_id}")
        return file_id

async def main():
    print("=" * 70)
    print("🎬 VIDEO YUKLASH VA FILE_ID OLISH")
    print("=" * 70)
    print()
    
    bot = Bot(token=TOKEN)
    file_ids = {}
    
    try:
        for key, url in VIDEOS_TO_UPLOAD.items():
            filename = f"temp_{key}.mp4"
            
            # 1. URL dan yuklab olish
            if await download_video(url, filename):
                # 2. Telegram ga yuklash
                file_id = await upload_to_telegram(bot, filename, key)
                file_ids[key] = file_id
                
                # 3. Temp faylni o'chirish
                os.remove(filename)
                print(f"🗑 Temp fayl o'chirildi: {filename}\n")
        
        print("=" * 70)
        print("✅ BARCHA VIDEOLAR YUKLANDI!")
        print("=" * 70)
        print()
        print("📋 FILE_ID LAR:")
        print()
        for key, file_id in file_ids.items():
            print(f"{key}:")
            print(f'    "file_id": "{file_id}",')
            print()
        
        print("📝 Bu file_id larni handlers/videos.py ga ko'chiring!")
        
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
