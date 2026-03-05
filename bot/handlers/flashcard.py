"""
Flashcard - so'zlarni samarali o'rganish rejimi
"""
import json
import random
from pathlib import Path
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline_menus import get_flashcard_keyboard, get_words_menu_inline
from services.db import get_user_level

router = Router()

# So'zlarni yuklash
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
with open(DATA_DIR / "words.json", "r", encoding="utf-8") as f:
    WORDS = json.load(f)

# Flashcard holati
FLASHCARD_STATE = {}
# Sevimli so'zlar (user_id: [word_ids])
FAVORITES = {}


@router.callback_query(F.data == "words:flashcard")
async def start_flashcard(callback: CallbackQuery):
    """Flashcard rejimini boshlash"""
    user_id = callback.from_user.id
    user_level = get_user_level(user_id) or "beginner"
    
    # Foydalanuvchi darajasiga mos so'zlar
    level_words = [w for w in WORDS if w.get("level") == user_level]
    
    if not level_words:
        await callback.answer("❌ Bu daraja uchun so'zlar yo'q", show_alert=True)
        return
    
    # Random tartibda aralashtiramiz
    random.shuffle(level_words)
    
    # Holatni saqlaymiz
    FLASHCARD_STATE[user_id] = {
        "words": level_words,
        "current_index": 0,
        "known_count": 0,
        "unknown_count": 0,
        "revealed": False
    }
    
    await show_flashcard(callback, user_id)


async def show_flashcard(callback: CallbackQuery, user_id: int):
    """Flashcard ko'rsatish"""
    if user_id not in FLASHCARD_STATE:
        await callback.answer("❌ Flashcard rejimi aktiv emas", show_alert=True)
        return
    
    state = FLASHCARD_STATE[user_id]
    words = state["words"]
    current_index = state["current_index"]
    
    if current_index >= len(words):
        # Flashcard tugadi
        known = state["known_count"]
        unknown = state["unknown_count"]
        total = known + unknown
        percentage = (known / total * 100) if total > 0 else 0
        
        await callback.message.edit_text(
            f"🎉 <b>Flashcard tugadi!</b>\n\n"
            f"📊 Natijalar:\n"
            f"✅ Bilgan: {known}\n"
            f"❌ Bilmagan: {unknown}\n"
            f"📈 Foiz: {percentage:.1f}%\n\n"
            f"💪 Ajoyib! Davom eting!",
            reply_markup=get_words_menu_inline(),
            parse_mode="HTML"
        )
        
        del FLASHCARD_STATE[user_id]
        await callback.answer()
        return
    
    word = words[current_index]
    revealed = state.get("revealed", False)
    
    # Sevimli belgisi
    is_favorite = user_id in FAVORITES and word.get("word") in FAVORITES[user_id]
    fav_icon = "⭐" if is_favorite else ""
    
    if revealed:
        # Javob ko'rsatilgan
        text = (
            f"📖 <b>Flashcard #{current_index + 1}</b> {fav_icon}\n\n"
            f"🔤 <b>So'z:</b> {word['word']}\n"
            f"📝 <b>Ma'no:</b> {word['meaning']}\n\n"
            f"❓ Bu so'zni bilasmanni?"
        )
    else:
        # Faqat so'zni ko'rsatish
        text = (
            f"📖 <b>Flashcard #{current_index + 1}</b> {fav_icon}\n\n"
            f"🔤 <b>So'z:</b> {word['word']}\n\n"
            f"💡 Ma'nosini bilamanlar javobni ko'rsatamang!\n"
            f"🔍 Javobni ko'rish uchun tugmani bosing."
        )
    
    keyboard = get_flashcard_keyboard(
        word_id=word.get("word"),
        total_words=len(words),
        current_index=current_index
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("flashcard:reveal:"))
async def reveal_flashcard(callback: CallbackQuery):
    """Javobni ko'rsatish"""
    user_id = callback.from_user.id
    
    if user_id in FLASHCARD_STATE:
        FLASHCARD_STATE[user_id]["revealed"] = True
        await show_flashcard(callback, user_id)
    else:
        await callback.answer("❌ Flashcard rejimi aktiv emas", show_alert=True)


@router.callback_query(F.data.startswith("flashcard:known:"))
async def mark_as_known(callback: CallbackQuery):
    """Bildim deb belgilash"""
    user_id = callback.from_user.id
    
    if user_id not in FLASHCARD_STATE:
        await callback.answer("❌ Flashcard rejimi aktiv emas", show_alert=True)
        return
    
    state = FLASHCARD_STATE[user_id]
    state["known_count"] += 1
    state["current_index"] += 1
    state["revealed"] = False
    
    await callback.answer("✅ Ajoyib!", show_alert=False)
    await show_flashcard(callback, user_id)


@router.callback_query(F.data.startswith("flashcard:unknown:"))
async def mark_as_unknown(callback: CallbackQuery):
    """Bilmadim deb belgilash"""
    user_id = callback.from_user.id
    
    if user_id not in FLASHCARD_STATE:
        await callback.answer("❌ Flashcard rejimi aktiv emas", show_alert=True)
        return
    
    state = FLASHCARD_STATE[user_id]
    state["unknown_count"] += 1
    state["current_index"] += 1
    state["revealed"] = False
    
    await callback.answer("💪 Davom eting!", show_alert=False)
    await show_flashcard(callback, user_id)


@router.callback_query(F.data.startswith("flashcard:fav:"))
async def toggle_favorite(callback: CallbackQuery):
    """Sevimlilikka qo'shish/olib tashlash"""
    user_id = callback.from_user.id
    word = callback.data.split(":")[2]
    
    if user_id not in FAVORITES:
        FAVORITES[user_id] = []
    
    if word in FAVORITES[user_id]:
        FAVORITES[user_id].remove(word)
        await callback.answer("❌ Sevimlilardan olib tashlandi", show_alert=False)
    else:
        FAVORITES[user_id].append(word)
        await callback.answer("⭐ Sevimlilarga qo'shildi!", show_alert=False)
    
    # Yangilash
    if user_id in FLASHCARD_STATE:
        await show_flashcard(callback, user_id)


@router.callback_query(F.data.startswith("flashcard:next:"))
async def next_flashcard(callback: CallbackQuery):
    """Keyingi flashcard"""
    user_id = callback.from_user.id
    
    if user_id not in FLASHCARD_STATE:
        await callback.answer("❌ Flashcard rejimi aktiv emas", show_alert=True)
        return
    
    state = FLASHCARD_STATE[user_id]
    if state["current_index"] < len(state["words"]) - 1:
        state["current_index"] += 1
        state["revealed"] = False
        await show_flashcard(callback, user_id)
    else:
        await callback.answer("❌ Oxirgi flashcard", show_alert=True)


@router.callback_query(F.data.startswith("flashcard:prev:"))
async def prev_flashcard(callback: CallbackQuery):
    """Oldingi flashcard"""
    user_id = callback.from_user.id
    
    if user_id not in FLASHCARD_STATE:
        await callback.answer("❌ Flashcard rejimi aktiv emas", show_alert=True)
        return
    
    state = FLASHCARD_STATE[user_id]
    if state["current_index"] > 0:
        state["current_index"] -= 1
        state["revealed"] = False
        await show_flashcard(callback, user_id)
    else:
        await callback.answer("❌ Birinchi flashcard", show_alert=True)


@router.callback_query(F.data == "flashcard:stats")
async def show_flashcard_stats(callback: CallbackQuery):
    """Flashcard statistika"""
    user_id = callback.from_user.id
    
    if user_id not in FLASHCARD_STATE:
        await callback.answer("❌ Flashcard rejimi aktiv emas", show_alert=True)
        return
    
    state = FLASHCARD_STATE[user_id]
    known = state["known_count"]
    unknown = state["unknown_count"]
    current = state["current_index"] + 1
    total = len(state["words"])
    
    await callback.answer(
        f"📊 Progress: {current}/{total}\n"
        f"✅ Bilgan: {known}\n"
        f"❌ Bilmagan: {unknown}",
        show_alert=True
    )


def register(dp):
    dp.include_router(router)
