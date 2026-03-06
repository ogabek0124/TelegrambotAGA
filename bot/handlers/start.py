import asyncio

from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from keyboards.inline_menus import get_main_menu_inline
from services.db import add_referral, get_referrals_count, get_user_level
from services.user_sync import async_sync_telegram_user

router = Router()
_BOT_USERNAME: str | None = None


@router.message(CommandStart())
async def start_handler(message: types.Message, command: CommandObject | None = None):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username

    await message.answer("⏳ Yuklanmoqda...")

    # Blocking sync is moved to thread so first response is fast.
    asyncio.create_task(async_sync_telegram_user(user_id, username, first_name))

    referred = False
    if command and command.args and command.args.isdigit():
        referrer_id = int(command.args)
        referred = add_referral(user_id, referrer_id)

    global _BOT_USERNAME
    if not _BOT_USERNAME:
        _BOT_USERNAME = (await message.bot.get_me()).username
    referral_link = f"https://t.me/{_BOT_USERNAME}?start={user_id}"
    
    user_level = get_user_level(user_id)
    
    if user_level:
        referrals_count = get_referrals_count(user_id)

        referral_line = (
            f"\n🎁 Referal bonusingiz qabul qilindi!"
            if referred
            else ""
        )

        await message.answer(
            f"👋 Salom, {first_name}!\n\n"
            f"📊 Sizning darajangiz: <b>{user_level.capitalize()}</b>\n"
            f"🔗 Referal linkingiz:\n<code>{referral_link}</code>\n"
            f"👥 Referallar soni: <b>{referrals_count}</b>{referral_line}\n\n"
            f"🚀 Nima qilishni xohlaysiz?",
            reply_markup=get_main_menu_inline(),
            parse_mode="HTML"
        )
    else:
        referral_line = "\n🎁 Siz referal orqali qo'shildingiz!" if referred else ""
        await message.answer(
            f"👋 <b>{first_name}</b>, InglizchaOson botiga xush kelibsiz!\n\n"
            f"🎓 Birinchi o'rinda darajangizni tanlang:\n"
            f"🔗 Do'stlarga ulashish: <code>{referral_link}</code>\n"
            f"{referral_line}\n"
            f"📚 So'ngra o'rganishni boshlang!",
            reply_markup=get_main_menu_inline(),
            parse_mode="HTML"
        )


def register(dp):
    dp.include_router(router)

