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


@router.message(lambda m: m.text == "📚 Grammar")
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

    await message.answer(
        f"📘 {g['title']}\n\n"
        f"📖 Qoida:\n{g['rule']}\n\n"
        f"✏️ Misol:\n{g['example']}\n\n"
        f"💡 Tushuntirish:\n{g['explanation']}",
        reply_markup=grammar_menu
    )


def register(dp):
    dp.include_router(router)
