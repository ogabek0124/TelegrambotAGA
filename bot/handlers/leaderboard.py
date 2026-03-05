from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from keyboards.inline_menus import get_main_menu_inline
from services.db import get_leaderboard

router = Router()


@router.callback_query(F.data == "menu:leaderboard")
async def show_leaderboard(callback: CallbackQuery):
    leaders = get_leaderboard(limit=10)

    if not leaders:
        await callback.message.edit_text(
            "❗ Leaderboard bo'sh",
            reply_markup=get_main_menu_inline()
        )
        await callback.answer()
        return

    text = "🏆 <b>Top 10 O'quvchilar</b>\n\n"
    for i, leader in enumerate(leaders, 1):
        user_id, streak, total = leader
        text += f"{i}. Foydalanuvchi #{user_id}: {streak}🔥 ({total} so'z)\n"

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_main_menu_inline())
    await callback.answer()


def register(dp):
    dp.include_router(router)
