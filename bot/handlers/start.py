from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from keyboards.inline_menus import get_main_menu_inline
from services.db import get_user_level
from services.user_sync import sync_telegram_user
from services.db import upsert_user, register_referral, get_referral_stats
from config import BOT_USERNAME

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username

    # Keep local analytics/user registry fresh for stats and broadcast.
    upsert_user(user_id, username, first_name)
    
    # Sync user to Django admin
    sync_telegram_user(user_id, username, first_name)

    referral_note = ""
    if command and command.args and command.args.isdigit():
        referrer_id = int(command.args)
        if register_referral(user_id, referrer_id):
            referral_note = "\n\n🎁 Siz referal orqali qo'shildingiz!"
    
    user_level = get_user_level(user_id)
    
    if user_level:
        await message.answer(
            f"👋 Salom, {first_name}!\n\n"
            f"📊 Sizning darajangiz: <b>{user_level.capitalize()}</b>\n"
            f"🚀 Nima qilishni xohlaysiz?{referral_note}",
            reply_markup=get_main_menu_inline(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"👋 <b>{first_name}</b>, InglizchaOson botiga xush kelibsiz!\n\n"
            f"🎓 Birinchi o'rinda darajangizni tanlang:\n"
            f"📚 So'ngra o'rganishni boshlang!{referral_note}",
            reply_markup=get_main_menu_inline(),
            parse_mode="HTML"
        )


@router.message(Command("referral"))
async def referral_handler(message: types.Message):
    if BOT_USERNAME:
        link = f"https://t.me/{BOT_USERNAME}?start={message.from_user.id}"
    else:
        link = f"t.me/yourbot?start={message.from_user.id}"

    stats = get_referral_stats(message.from_user.id)

    await message.answer(
        "🔗 <b>Sizning referral linkingiz</b>\n\n"
        f"{link}\n\n"
        "Do'stlaringiz shu link orqali kirsa sizga bonus yoziladi.\n\n"
        f"👥 Taklif qilganlar: <b>{stats['referral_count']}</b>\n"
        f"🎁 Bonus: <b>{stats['bonus']}</b>",
        parse_mode="HTML"
    )


def register(dp):
    dp.include_router(router)

