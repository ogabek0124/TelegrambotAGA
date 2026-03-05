"""
Callback query handler - inline button'lar uchun
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline_menus import (
    get_main_menu_inline,
    get_level_menu_inline,
    get_words_menu_inline,
    get_test_menu_inline,
    get_grammar_menu_inline,
    get_books_level_menu_inline,
    get_word_categories_inline
)
from services.db import set_user_level, get_user_level, get_progress, get_streak
from services.user_sync import update_user_progress

router = Router()


@router.callback_query(F.data.startswith("menu:"))
async def handle_menu_navigation(callback: CallbackQuery):
    """Menyu navigatsiya"""
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
    
    elif action == "grammar":
        await callback.message.edit_text(
            f"📖 Grammar bo'limi\n"
            f"Darajangiz: <b>{user_level.capitalize()}</b>\n\n"
            f"Tanlang:",
            parse_mode="HTML",
            reply_markup=get_grammar_menu_inline()
        )
    
    elif action == "books":
        await callback.message.edit_text(
            "📚 Kitoblar\n\n"
            "Darajangizni tanlang:",
            reply_markup=get_books_level_menu_inline()
        )
    
    elif action == "progress":
        user_id = callback.from_user.id
        progress = get_progress(user_id)
        
        if not progress:
            await callback.message.edit_text(
                "📊 Sizda hali progress yo'q.\n\n"
                "Testlarni yechib boshlang! 🚀",
                reply_markup=get_main_menu_inline()
            )
        else:
            correct, total, streak, last_date = progress
            percentage = (correct / total) * 100 if total > 0 else 0
            
            await callback.message.edit_text(
                f"📊 <b>Sizning progressingiz</b>\n\n"
                f"✅ To'g'ri: {correct}/{total}\n"
                f"📈 Foiz: {percentage:.1f}%\n"
                f"🔥 Streak: {streak} kun\n"
                f"📅 Oxirgi faollik: {last_date}",
                parse_mode="HTML",
                reply_markup=get_main_menu_inline()
            )
    
    elif action == "leaderboard":
        from services.db import get_leaderboard
        leaders = get_leaderboard(limit=10)
        
        if not leaders:
            text = "🏆 Leaderboard bo'sh\n\n Birinchi bo'ling!"
        else:
            text = "🏆 <b>Top 10 Leaderboard</b>\n\n"
            for i, (username, correct, total) in enumerate(leaders, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                text += f"{emoji} {username}: {correct}/{total}\n"
        
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_main_menu_inline()
        )
    
    elif action == "streak":
        user_id = callback.from_user.id
        streak = get_streak(user_id)
        
        if streak >= 7:
            badge = "🔥 Hot Streak!"
        elif streak >= 3:
            badge = "⭐ Good job!"
        else:
            badge = "🌱 Keep going!"
        
        await callback.message.edit_text(
            f"🔥 <b>Sizning Streak'ingiz</b>\n\n"
            f"📅 Ketma-ket kunlar: <b>{streak}</b>\n"
            f"{badge}\n\n"
            f"Har kuni test yechib, streak'ni oshiring! 💪",
            parse_mode="HTML",
            reply_markup=get_main_menu_inline()
        )
    
    elif action == "videos":
        await callback.message.edit_text(
            "🎥 <b>Videolar bo'limi</b>\n\n"
            "Tez orada qo'shiladi...",
            parse_mode="HTML",
            reply_markup=get_main_menu_inline()
        )
    
    elif action == "achievements":
        from handlers.achievements_handler import show_achievements
        await show_achievements(callback)
        return
    
    await callback.answer()


@router.callback_query(F.data.startswith("level:"))
async def handle_level_selection(callback: CallbackQuery):
    """Daraja tanlash"""
    level = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    set_user_level(user_id, level)
    update_user_progress(telegram_id=user_id, level=level)
    
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
    await callback.message.edit_text(
        "📂 <b>So'z kategoriyalari</b>\n\n"
        "Qaysi kategoriyani o'rganmoqchisiz?",
        parse_mode="HTML",
        reply_markup=get_word_categories_inline()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back:"))
async def handle_back_navigation(callback: CallbackQuery):
    """Orqaga qaytish"""
    destination = callback.data.split(":")[1]
    
    if destination == "main":
        user_level = get_user_level(callback.from_user.id) or "beginner"
        await callback.message.edit_text(
            f"🏠 <b>Asosiy menyu</b>\n\n"
            f"📊 Darajangiz: {user_level.capitalize()}",
            parse_mode="HTML",
            reply_markup=get_main_menu_inline()
        )
    
    await callback.answer()


def register(dp):
    dp.include_router(router)
