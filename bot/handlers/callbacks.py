"""
Callback query handler - inline button'lar uchun
"""
import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline_menus import (
    get_main_menu_inline,
    get_level_menu_inline,
    get_words_menu_inline,
    get_test_menu_inline,
    get_grammar_menu_inline,
    get_books_level_menu_inline,
    get_word_categories_inline
)
from services.db import set_user_level, get_user_level
from services.user_sync import async_update_user_progress

router = Router()


@router.callback_query(F.data.in_({"menu:level", "menu:words", "menu:test", "menu:books", "menu:videos"}))
async def handle_menu_navigation(callback: CallbackQuery):
    """Menyu navigatsiya"""
    await callback.answer("⏳ Yuklanmoqda...")
    action = callback.data.split(":")[1]
    user_level = get_user_level(callback.from_user.id) or "beginner"
    
    if action == "level":
        await callback.message.edit_text(
            f"📊 Hozirgi darajangiz: <b>{user_level.capitalize()}</b>\n\n"
            f"Darajani o'zgartirish:",
            parse_mode="HTML",
            reply_markup=get_level_menu_inline()
        )
    
    elif action == "words":
        await callback.message.edit_text(
            f"📚 So'zlar bo'limi\n"
            f"Darajangiz: <b>{user_level.capitalize()}</b>\n\n"
            f"Tanlang:",
            parse_mode="HTML",
            reply_markup=get_words_menu_inline()
        )
    
    elif action == "test":
        await callback.message.edit_text(
            f"📝 Test bo'limi\n"
            f"Darajangiz: <b>{user_level.capitalize()}</b>\n\n"
            f"Test turini tanlang:",
            parse_mode="HTML",
            reply_markup=get_test_menu_inline()
        )
    
    elif action == "books":
        await callback.message.edit_text(
            "📚 Kitoblar\n\n"
            "Darajangizni tanlang:",
            reply_markup=get_books_level_menu_inline()
        )
    
    elif action == "videos":
        back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
        ])
        await callback.message.edit_text(
            "🎥 <b>Videolar bo'limi</b>\n\n"
            "Tez orada qo'shiladi...",
            parse_mode="HTML",
            reply_markup=back_keyboard
        )
    



@router.callback_query(F.data.startswith("level:"))
async def handle_level_selection(callback: CallbackQuery):
    """Daraja tanlash"""
    await callback.answer("⏳ Yuklanmoqda...")
    level = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    set_user_level(user_id, level)
    asyncio.create_task(async_update_user_progress(telegram_id=user_id, level=level))
    
    await callback.message.edit_text(
        f"✅ Darajangiz o'rnatildi: <b>{level.capitalize()}</b>\n\n"
        f"Endi siz {level} darajasiga mos kontentni ko'rasiz!",
        parse_mode="HTML",
        reply_markup=get_main_menu_inline()
    )
    await callback.answer(f"✅ {level.capitalize()} darajasi tanlandi!")


@router.callback_query(F.data == "words:categories")
async def handle_word_categories(callback: CallbackQuery):
    """So'z kategoriyalari"""
    await callback.answer("🔍 Qidirilmoqda...")
    await callback.message.edit_text(
        "📂 <b>So'z kategoriyalari</b>\n\n"
        "Qaysi kategoriyani o'rganmoqchisiz?",
        parse_mode="HTML",
        reply_markup=get_word_categories_inline()
    )



@router.callback_query(F.data.startswith("back:"))
async def handle_back_navigation(callback: CallbackQuery):
    """Orqaga qaytish"""
    await callback.answer("⏳ Yuklanmoqda...")
    destination = callback.data.split(":")[1]
    
    if destination == "main":
        user_level = get_user_level(callback.from_user.id) or "beginner"
        await callback.message.edit_text(
            f"🏠 <b>Asosiy menyu</b>\n\n"
            f"📊 Darajangiz: {user_level.capitalize()}",
            parse_mode="HTML",
            reply_markup=get_main_menu_inline()
        )



def register(dp):
    dp.include_router(router)
