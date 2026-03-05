from aiogram import Router, types
from keyboards.menus import main_menu
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


@router.message(lambda m: m.text and "Progress" in m.text)
async def show_progress(message: types.Message):
    user_id = message.from_user.id
    progress = get_progress(user_id)

    if not progress:
        await message.answer(
            "Sizda hali progress yo'q. Testlarni yeching!",
            reply_markup=main_menu
        )
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

    await message.answer(
        f"SIZNING STATISTIKA\n\n"
        f"Test Natijalari:\n"
        f"✅ To'g'ri: {correct}/{total}\n"
        f"📈 Foiz: {percentage:.1f}%\n\n"
        f"Motivatsiya:\n"
        f"🔥 Streak: {streak} kun\n"
        f"{badge}\n\n"
        f"Darajasi: {level}\n"
        f"Oxirgi sana: {last_date}",
        reply_markup=main_menu
    )


def register(dp):
    dp.include_router(router)
