"""  
Test tarixi - o'tgan testlar natijalari
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.test_history import get_test_history, get_test_stats
from datetime import datetime

router = Router()


@router.callback_query(F.data == "test:history")
async def show_test_history(callback: CallbackQuery):
    """Test tarixini ko'rsatish"""
    user_id = callback.from_user.id
    
    # Statistika
    stats = get_test_stats(user_id)
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
    ])
    
    if not stats or stats[0] == 0:
        await callback.message.edit_text(
            "📊 <b>Test Tarixi</b>\n\n"
            "Siz hali test yechmagansiz.\n"
            "Birinchi testni yeching! 💪",
            parse_mode="HTML",
            reply_markup=back_keyboard
        )
        await callback.answer()
        return
    
    total_tests, total_correct, total_questions, avg_percentage = stats
    
    # Oxirgi 10 ta test
    history = get_test_history(user_id, limit=10)
    
    text = f"📊 <b>Test Tarixi</b>\n\n"
    text += f"📈 <b>Umumiy Statistika:</b>\n"
    text += f"   • Testlar soni: {total_tests}\n"
    text += f"   • To'g'ri javoblar: {total_correct}/{total_questions}\n"
    text += f"   • O'rtacha foiz: {avg_percentage:.1f}%\n\n"
    
    if history:
        text += f"📋 <b>Oxirgi 10 ta test:</b>\n\n"
        
        test_type_emoji = {
            "vocabulary": "📘",
            "grammar": "📗",
            "listening": "🎧",
            "mixed": "🎲"
        }
        
        for i, (test_type, difficulty, correct, total, time_spent, completed_at) in enumerate(history, 1):
            emoji = test_type_emoji.get(test_type, "📝")
            percentage = (correct / total) * 100 if total > 0 else 0
            
            # Vaqtni formatlash
            if isinstance(completed_at, str):
                try:
                    completed_at = datetime.fromisoformat(completed_at)
                except:
                    pass
            
            date_str = completed_at.strftime("%d.%m.%Y") if isinstance(completed_at, datetime) else str(completed_at)
            
            text += f"{i}. {emoji} {test_type.capitalize()} ({difficulty})\n"
            text += f"   ✅ {correct}/{total} ({percentage:.0f}%)"
            
            if time_spent:
                text += f" • ⏱ {time_spent // 60}:{time_spent % 60:02d}"
            
            text += f"\n   📅 {date_str}\n\n"
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=back_keyboard
    )
    await callback.answer()


def register(dp):
    dp.include_router(router)
