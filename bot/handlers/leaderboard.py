from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.db import get_leaderboard

router = Router()


@router.callback_query(F.data == "menu:leaderboard")
async def show_leaderboard(callback: CallbackQuery):
    leaders = get_leaderboard(limit=10)
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
    ])

    if not leaders:
        await callback.message.edit_text(
            "❗ Leaderboard bo'sh",
            reply_markup=back_keyboard
        )
        await callback.answer()
        return
    
    text = "🏆 <b>Top 10 O'quvchilar</b>\n\n"
    for i, leader in enumerate(leaders, 1):
        user_id, streak, total = leader
        text += f"{i}. Foydalanuvchi #{user_id}: {streak}🔥 ({total} so'z)\n"

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_keyboard)
    await callback.answer()


def register(dp):
    dp.include_router(router)
