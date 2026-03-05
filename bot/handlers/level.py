from aiogram import Router, types
from keyboards.menus import main_menu
from keyboards.level_menu import level_menu
from services.db import set_user_level, get_user_level

router = Router()


@router.message(lambda m: m.text and "tanlash" in m.text and ("Draja" in m.text or "Daraja" in m.text))
async def choose_level(message: types.Message):
    user_id = message.from_user.id
    level = get_user_level(user_id)

    if level:
        await message.answer(
            f"✅ Hozirgi darajangiz: {level.capitalize()}\n"
            f"Boshqa drajani tanlaysizmi?",
            reply_markup=level_menu
        )
    else:
        await message.answer(
            "📊 Darajangizni tanlang:\n\n"
            "🟢 Beginner - Yangi boshlanuvchilar\n"
            "🟡 Intermediate - O'rta darajasi\n"
            "🔴 IELTS - Yuqori daraja",
            reply_markup=level_menu
        )


@router.message(lambda m: m.text in ["🟢 Beginner", "🟡 Intermediate", "🔴 IELTS", "◀️ Ortga"])
async def save_level(message: types.Message):
    text = message.text

    if text == "◀️ Ortga":
        await message.answer("🏠 Asosiy menu", reply_markup=main_menu)
        return

    if "Beginner" in text:
        level = "beginner"
    elif "Intermediate" in text:
        level = "intermediate"
    elif "IELTS" in text:
        level = "ielts"
    else:
        return

    user_id = message.from_user.id
    set_user_level(user_id, level)

    await message.answer(
        f"🎉 Darajangiz saqlandi: {level.capitalize()}\n\n"
        f"Endi siz {level.capitalize()} darajasiga mos testlarni yechishingiz mumkin! 🚀",
        reply_markup=main_menu
    )


def register(dp):
    dp.include_router(router)

