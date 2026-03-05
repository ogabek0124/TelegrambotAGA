"""
Achievements handler - yutuqlarni ko'rsatish
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.achievements import (
    get_user_achievements,
    get_achievement_progress,
    ACHIEVEMENTS
)
from keyboards.inline_menus import get_main_menu_inline

router = Router()


@router.callback_query(F.data == "menu:achievements")
async def show_achievements(callback: CallbackQuery):
    """Yutuqlarni ko'rsatish"""
    user_id = callback.from_user.id
    
    # Progress
    progress = get_achievement_progress(user_id)
    earned_achievements = get_user_achievements(user_id)
    earned_ids = [ach[0] for ach in earned_achievements]
    
    text = f"🏆 <b>Yutuqlar</b>\n\n"
    text += f"📊 Progress: {progress['earned_achievements']}/{progress['total_achievements']}\n"
    text += f"⭐ Ochko: {progress['earned_points']}/{progress['total_points']}\n"
    text += f"📈 Foiz: {progress['percentage']:.1f}%\n\n"
    
    text += f"━━━━━━━━━━━━━━━━\n\n"
    
    # Bo'sh yutuqlar
    text += f"<b>Ochilmagan yutuqlar:</b>\n\n"
    for ach_id, ach_data in ACHIEVEMENTS.items():
        if ach_id not in earned_ids:
            text += f"{ach_data['icon']} <b>{ach_data['title']}</b>\n"
            text += f"   {ach_data['description']}\n"
            text += f"   💰 {ach_data['points']} ochko\n\n"
    
    text += f"━━━━━━━━━━━━━━━━\n\n"
    
    # Ochilgan yutuqlar
    if earned_ids:
        text += f"<b>Ochilgan yutuqlar:</b>\n\n"
        for ach_id in earned_ids:
            if ach_id in ACHIEVEMENTS:
                ach_data = ACHIEVEMENTS[ach_id]
                text += f"✅ {ach_data['icon']} <b>{ach_data['title']}</b>\n"
                text += f"   {ach_data['description']}\n"
                text += f"   💰 {ach_data['points']} ochko\n\n"
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
    ])
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=back_keyboard
    )
    await callback.answer()


def register(dp):
    dp.include_router(router)
