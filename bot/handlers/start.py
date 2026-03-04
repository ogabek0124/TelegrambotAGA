from aiogram import Router, types
from aiogram.filters import Command
from keyboards.menus import main_menu
from services.db import get_user_level

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    user_level = get_user_level(user_id)
    
    if user_level:
        await message.answer(
            f"👋 Salom, {first_name}!\n\n"
            f"📊 Sizning daraja: {user_level.capitalize()}\n"
            f"Davom etaylik? 🚀",
            reply_markup=main_menu
        )
    else:
        await message.answer(
            f"👋 {first_name}, InglizchaOson botiga xush kelibsiz!\n\n"
            f"🎓 Engilaylik, birinchi o'rinda darajangizni tanlang:",
            reply_markup=main_menu
        )


def register(dp):
    dp.include_router(router)

