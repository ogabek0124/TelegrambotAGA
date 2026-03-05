import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import TOKEN
from services.db import init_db
from handlers import start, level, words, test, grammar, progress, leaderboard, daily, streak, videos

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logger.info("Logger tayyorlandi")

# Bot va Dispatcher
logger.info("Bot va Dispatcher yaratilmoqda...")
bot = Bot(token=TOKEN)
dp = Dispatcher()
logger.info("Bot va Dispatcher tayyorlandi")

# Handlers registration
logger.info("Handlers ro'yxatga olinmoqda...")
start.register(dp)
logger.info("✓ start handler")
level.register(dp)
logger.info("✓ level handler")
words.register(dp)
logger.info("✓ words handler")
test.register(dp)
logger.info("✓ test handler")
grammar.register(dp)
logger.info("✓ grammar handler")
progress.register(dp)
logger.info("✓ progress handler")
leaderboard.register(dp)
logger.info("✓ leaderboard handler")
daily.register(dp)
logger.info("✓ daily handler")
streak.register(dp)
logger.info("✓ streak handler")
videos.register(dp)
logger.info("✓ videos handler")
logger.info("Barcha handlers ro'yxatga olingan!")


async def set_default_commands(bot: Bot):
    """Bot commands ni o'rnatish"""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam"),
    ]
    await bot.set_my_commands(commands)


async def start_healthcheck_server():
    """Render Web Service uchun oddiy HTTP health endpoint."""
    async def handle_client(reader, writer):
        try:
            await reader.read(1024)
            body = b"OK"
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Content-Length: 2\r\n"
                b"Connection: close\r\n\r\n" + body
            )
            writer.write(response)
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    port = int(os.getenv("PORT", "10000"))
    server = await asyncio.start_server(handle_client, host="0.0.0.0", port=port)
    logger.info(f"Healthcheck server ishga tushdi: 0.0.0.0:{port}")
    return server


async def main():
    health_server = None
    try:
        # Render Web Service timeout bo'lmasligi uchun port ochamiz.
        health_server = await start_healthcheck_server()

        # DB init (sync, lekin async context da)
        print("[*] Database tayyorlanmoqda...")
        init_db()
        print("[✓] Database tayyorlandi")
        
        # Bot commands'ni o'rnatish
        print("[*] Bot commands o'rnatilmoqda...")
        await set_default_commands(bot)
        print("[✓] Bot commands o'rnatildi")
        
        print("\n" + "="*50)
        print("⭐ BOT MUVAFFAQIYATLI ISHGA TUSHDI! ⭐")
        print("="*50)
        print("🔄 Telegram'dan xabarlar kutilmoqda...")
        print("💬 Test qilish uchun: @inglizchaoson_bot ga /start yozing\n")

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        print(f"\n❌ XATO YUZAGA KELDI: {e}")
        logger.exception("Bot xatosi")
    finally:
        if health_server is not None:
            health_server.close()
            await health_server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
