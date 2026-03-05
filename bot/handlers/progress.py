from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.db import get_progress, get_connection, get_streak

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


@router.callback_query(F.data == "menu:progress")
async def show_progress(callback: CallbackQuery):
    user_id = callback.from_user.id
    progress = get_progress(user_id)
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
    ])

    if not progress:
        await callback.message.edit_text(
            "Sizda hali progress yo'q. Testlarni yeching!",
            reply_markup=back_keyboard
        )
        await callback.answer()
        return

    correct, total, streak, last_date = progress
    percentage = (correct / total) * 100 if total > 0 else 0
    
    # Level olish
    level = "Beginner"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT level FROM progress WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if row and row[0]:
            level = row[0].capitalize()
    
    # Badge
    badge = get_badge(streak)

    from keyboards.inline_menus import InlineKeyboardMarkup, InlineKeyboardButton
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
    ])
    
    await callback.message.edit_text(
        f"📊 <b>SIZNING STATISTIKA</b>\n\n"
        f"<b>Test Natijalari:</b>\n"
        f"✅ To'g'ri: {correct}/{total}\n"
        f"📈 Foiz: {percentage:.1f}%\n\n"
        f"<b>Motivatsiya:</b>\n"
        f"🔥 Streak: {streak} kun\n"
        f"{badge}\n\n"
        f"<b>Darajasi:</b> {level}\n"
        f"<b>Oxirgi sana:</b> {last_date}",
        parse_mode="HTML",
        reply_markup=back_keyboard
    )
    await callback.answer()


def register(dp):
    dp.include_router(router)
