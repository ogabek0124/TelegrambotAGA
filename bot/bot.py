import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import TOKEN
from services.db import init_db
from handlers import start, level, words, test, grammar, progress, leaderboard, daily, streak, videos

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot va Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Handlers registration
start.register(dp)
level.register(dp)
words.register(dp)
test.register(dp)
grammar.register(dp)
progress.register(dp)
leaderboard.register(dp)
daily.register(dp)
streak.register(dp)
videos.register(dp)


async def set_default_commands(bot: Bot):
    """Bot commands ni o'rnatish"""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam"),
    ]
    await bot.set_my_commands(commands)


async def main():
    # DB init (sync, lekin async context da)
    init_db()
    await set_default_commands(bot)
    print("Bot ishga tushdi...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
