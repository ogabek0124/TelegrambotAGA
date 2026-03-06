import json
from pathlib import Path
from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline_menus import get_main_menu_inline
from services.db import get_user_level

router = Router()

# Grammar yuklash
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

with open(DATA_DIR / "grammar.json", "r", encoding="utf-8") as f:
    GRAMMAR = json.load(f)

# ID mapping
GRAMMAR_MAP = {
    "1️⃣ Present Simple": "present_simple",
    "2️⃣ Past Simple": "past_simple",
    "3️⃣ Present Continuous": "present_continuous",
    "4️⃣ Will (Future)": "will_future",
    "5️⃣ Present Perfect": "present_perfect",
    "6️⃣ Present Perfect Cont.": "present_perfect_continuous",
    "7️⃣ Passive Voice": "passive_voice",
    "8️⃣ Conditional": "conditional_if",
    "9️⃣ Reported Speech": "reported_speech",
    "🔟 Inversion": "inversion",
}


@router.callback_query(F.data == "menu:grammar")
async def show_grammar_menu(callback: CallbackQuery):
    await callback.answer("⏳ Yuklanmoqda...")
    user_id = callback.from_user.id
    user_level = get_user_level(user_id) or "beginner"
    
    # Grammar inline keyboard
    grammar_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1️⃣ Present Simple", callback_data="grammar:present_simple")],
        [InlineKeyboardButton(text="2️⃣ Past Simple", callback_data="grammar:past_simple")],
        [InlineKeyboardButton(text="3️⃣ Present Continuous", callback_data="grammar:present_continuous")],
        [InlineKeyboardButton(text="4️⃣ Will (Future)", callback_data="grammar:will_future")],
        [InlineKeyboardButton(text="5️⃣ Present Perfect", callback_data="grammar:present_perfect")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
    ])
    
    await callback.message.edit_text(
        f"📚 <b>Grammar bo'limi</b>\n\n"
        f"Sizning daraja: <b>{user_level.capitalize()}</b>\n\n"
        f"Kerakli mavzuni tanlang:",
        parse_mode="HTML",
        reply_markup=grammar_keyboard
    )



@router.callback_query(F.data.startswith("grammar:"))
async def show_grammar(callback: CallbackQuery):
    await callback.answer("🔍 Qidirilmoqda...")
    grammar_id = callback.data.split(":")[1]

    # Find grammar
    g = next((x for x in GRAMMAR if x["id"] == grammar_id), None)
    if not g:
        await callback.answer("❌ Mavzu topilmadi", show_alert=True)
        return

    # Format response with new structure
    response = f"📘 <b>{g['title']}</b>\n\n"
    response += f"📖 <b>Qoida:</b>\n{g['rule']}\n\n"
    response += f"📝 <b>Struktura:</b>\n<code>{g['structure']}</code>\n\n"
    
    # Usage cases
    if 'usage' in g:
        response += "💡 <b>Ishlatilishi:</b>\n"
        for idx, use in enumerate(g['usage'], 1):
            response += f"{idx}. {use}\n"
        response += "\n"
    
    # Examples with translations
    if 'examples' in g:
        response += "✏️ <b>Misollar:</b>\n\n"
        for idx, ex in enumerate(g['examples'][:3], 1):  # First 3 examples
            response += f"{idx}. <i>{ex['english']}</i>\n"
            response += f"   {ex['uzbek']}\n"
            if 'note' in ex:
                response += f"   💭 {ex['note']}\n"
            response += "\n"
    
    # Common mistakes
    if 'common_mistakes' in g and g['common_mistakes']:
        response += "⚠️ <b>Keng tarqalgan xatolar:</b>\n"
        for mistake in g['common_mistakes'][:2]:  # First 2 mistakes  
            response += f"❌ {mistake['wrong']}\n"
            response += f"✅ {mistake['correct']}\n"
            if 'note' in mistake:
                response += f"   💬 {mistake['note']}\n"
            response += "\n"
    
    # Back button
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Grammar menyuga", callback_data="menu:grammar")],
        [InlineKeyboardButton(text="🏠 Asosiy menu", callback_data="back:main")]
    ])

    await callback.message.edit_text(
        response,
        reply_markup=back_keyboard,
        parse_mode="HTML"
    )



def register(dp):
    dp.include_router(router)
