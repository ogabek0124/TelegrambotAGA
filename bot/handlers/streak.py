from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from keyboards.inline_menus import get_main_menu_inline
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


@router.callback_query(F.data == "menu:streak")
async def show_streak(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    streak = get_streak(user_id)
    badge = get_badge(streak)
    
    await callback.message.edit_text(
        f"🔥 <b>YOUR STREAK</b>\n\n"
        f"<b>Streak:</b> {streak} kun\n"
        f"{badge}\n\n"
        f"Har kun darsga kilib streakingizni oshiring!",
        parse_mode="HTML",
        reply_markup=get_main_menu_inline()
    )
    await callback.answer()


def register(dp):
    dp.include_router(router)
