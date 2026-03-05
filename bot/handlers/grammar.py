import json
from pathlib import Path
from aiogram import Router, types
from keyboards.grammar_menu import grammar_menu
from keyboards.menus import main_menu
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


@router.message(lambda m: m.text and "Grammar" in m.text)
async def show_grammar_menu(message: types.Message):
    user_id = message.from_user.id
    user_level = get_user_level(user_id) or "beginner"
    
    await message.answer(
        f"📚 Grammar bo'limi\n"
        f"Sizning daraja: {user_level.capitalize()}\n"
        f"Kerakli mavzuni tanlang:",
        reply_markup=grammar_menu
    )


@router.message(lambda m: m.text in GRAMMAR_MAP.keys() or m.text == "◀️ Ortga")
async def show_grammar(message: types.Message):
    text = message.text
    
    if text == "◀️ Ortga":
        await message.answer("🏠 Asosiy menu", reply_markup=main_menu)
        return

    # Get grammar ID from mapping
    grammar_id = GRAMMAR_MAP.get(text)
    if not grammar_id:
        return

    # Find grammar
    g = next((x for x in GRAMMAR if x["id"] == grammar_id), None)
    if not g:
        await message.answer("❌ Mavzu topilmadi")
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

    await message.answer(
        response,
        reply_markup=grammar_menu,
        parse_mode="HTML"
    )


def register(dp):
    dp.include_router(router)
