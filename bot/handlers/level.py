from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from keyboards.inline_menus import get_level_menu_inline, get_main_menu_inline
from services.db import set_user_level, get_user_level
from services.user_sync import update_user_progress

router = Router()


@router.callback_query(F.data.startswith("level:"))
async def handle_level_selection(callback: CallbackQuery):
    """Inline button orqali daraja tanlash"""
    level = callback.data.split(":")[1]
    
    if level not in ["beginner", "intermediate", "ielts"]:
        await callback.answer("❌ Noto'g'ri daraja", show_alert=True)
        return
    
    user_id = callback.from_user.id
    set_user_level(user_id, level)
    
    # Django admin'ga sync qilish
    update_user_progress(telegram_id=user_id, level=level)
    
    level_names = {
        "beginner": "🟢 Beginner",
        "intermediate": "🟡 Intermediate",
        "ielts": "🔴 IELTS"
    }
    
    await callback.message.edit_text(
        f"🎉 Darajangiz saqlandi: <b>{level_names[level]}</b>\n\n"
        f"Endi siz {level.capitalize()} darajasiga mos:\n"
        f"• So'zlar bilan ishlashingiz\n"
        f"• Testlar yechishingiz\n"
        f"• Grammatika o'rganishingiz mumkin!\n\n"
        f"🚀 Davom etamiz?",
        reply_markup=get_main_menu_inline(),
        parse_mode="HTML"
    )
    
    await callback.answer("✅ Daraja saqlandi!", show_alert=False)


def register(dp):
    dp.include_router(router)

