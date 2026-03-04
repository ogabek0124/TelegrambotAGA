from aiogram import Router, types
from keyboards.menus import main_menu
from services.db import get_connection, get_streak

router = Router()


def get_badge(streak: int):
    """Streak soni bo'yicha badge berish"""
    if streak >= 30:
        return "💎 Legend (30+ kun)"
    elif streak >= 21:
        return "🏅 Champion (21+ kun)"
    elif streak >= 14:
        return "⭐ Master (14+ kun)"
    elif streak >= 7:
        return "🔥 Hot (7+ kun)"
    elif streak >= 3:
        return "🌟 Rising (3+ kun)"
    else:
        return "🆕 Beginner"


@router.message(lambda m: m.text and "Streakga" in m.text)
async def show_streak(message: types.Message):
    user_id = message.from_user.id
    
    streak = get_streak(user_id)
    badge = get_badge(streak)
    
    await message.answer(
        f"YOUR STREAK\n\n"
        f"Streak: {streak} kun\n"
        f"{badge}\n\n"
        f"Har kun darsga kilib streakingizni oshiring!",
        reply_markup=main_menu
    )


def register(dp):
    dp.include_router(router)
