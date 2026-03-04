from aiogram import Router, types
from keyboards.menus import main_menu
from services.db import get_leaderboard

router = Router()


@router.message(lambda m: m.text == "🏆 Leaderboard")
async def show_leaderboard(message: types.Message):
    leaders = get_leaderboard(limit=10)

    if not leaders:
        await message.answer(
            "❗ Leaderboard bo'sh",
            reply_markup=main_menu
        )
        return

    text = "🏆 Top 10 O'quvchilar\n\n"
    for i, leader in enumerate(leaders, 1):
        user_id, streak, total = leader
        text += f"{i}. Foydalanuvchi #{user_id}: {streak}🔥 ({total} so'z)\n"

    await message.answer(text, reply_markup=main_menu)


def register(dp):
    dp.include_router(router)
