"""
So'z kategoriyalari - turkumlarga ajratilgan so'zlar
"""
import json
from pathlib import Path
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline_menus import get_word_categories_inline, get_pagination_keyboard, get_words_menu_inline
from services.db import get_user_level

router = Router()

# So'zlarni yuklash
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
with open(DATA_DIR / "words.json", "r", encoding="utf-8") as f:
    WORDS = json.load(f)

# Kategoriya nomlari
CATEGORY_NAMES = {
    "family": "👨‍👩‍👧 Oila",
    "home": "🏠 Uy",
    "food": "🍔 Ovqat",
    "animals": "🐕 Hayvonlar",
    "nature": "🌳 Tabiat",
    "time": "⏰ Vaqt",
    "colors": "🎨 Ranglar",
    "body": "👤 Tana",
    "work": "💼 Ish",
    "technology": "📱 Texnologiya"
}

# Kategoriya state
CATEGORY_STATE = {}


@router.callback_query(F.data == "words:categories")
async def show_categories(callback: CallbackQuery):
    """Kategoriyalar ro'yxati"""
    await callback.message.edit_text(
        "🗂 <b>So'z kategoriyalari</b>\n\n"
        "Qaysi turkumdagi so'zlarni o'rganishni xohlaysiz?",
        reply_markup=get_word_categories_inline(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category:"))
async def show_category_words(callback: CallbackQuery):
    """Kategoriya bo'yicha so'zlar"""
    category = callback.data.split(":")[1]
    user_id = callback.from_user.id
    user_level = get_user_level(user_id) or "beginner"
    
    # Kategoriya bo'yicha so'zlarni filterlash
    # words.json'da category maydoni yo'q ekan, shuning uchun uni aniqlaymiz
    category_words = filter_words_by_category(category, user_level)
    
    if not category_words:
        await callback.answer(
            f"❌ {CATEGORY_NAMES.get(category, category)} kategoriyasida so'zlar yo'q",
            show_alert=True
        )
        return
    
    # State'ga saqlash
    CATEGORY_STATE[user_id] = {
        "category": category,
        "words": category_words,
        "page": 0
    }
    
    await show_category_page(callback, user_id)


async def show_category_page(callback: CallbackQuery, user_id: int):
    """Kategoriya sahifasini ko'rsatish"""
    if user_id not in CATEGORY_STATE:
        await callback.answer("❌ Kategoriya topilmadi", show_alert=True)
        return
    
    state = CATEGORY_STATE[user_id]
    category = state["category"]
    words = state["words"]
    page = state["page"]
    
    # Pagination
    per_page = 10
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_words = words[start_idx:end_idx]
    
    if not page_words:
        await callback.answer("❌ Bu sahifada so'zlar yo'q", show_alert=True)
        return
    
    # Matn yaratish
    category_name = CATEGORY_NAMES.get(category, category)
    total_pages = (len(words) + per_page - 1) // per_page
    
    text = f"🗂 <b>{category_name}</b>\n"
    text += f"📄 Sahifa {page + 1}/{total_pages} ({len(words)} ta so'z)\n"
    text += "─" * 30 + "\n\n"
    
    for idx, word in enumerate(page_words, start=start_idx + 1):
        text += f"{idx}. <b>{word['word']}</b>\n"
        text += f"   └─ {word['meaning']}\n\n"
    
    keyboard = get_pagination_keyboard(page, total_pages, f"category:{category}")
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category:") and F.data.contains(":page:"))
async def handle_category_pagination(callback: CallbackQuery):
    """Kategoriya sahifalarini almashtirish"""
    parts = callback.data.split(":")
    category = parts[1]
    
    if parts[3] == "current":
        await callback.answer()
        return
    
    page = int(parts[3])
    user_id = callback.from_user.id
    
    if user_id in CATEGORY_STATE:
        CATEGORY_STATE[user_id]["page"] = page
        await show_category_page(callback, user_id)
    else:
        await callback.answer("❌ Kategoriya topilmadi", show_alert=True)


def filter_words_by_category(category: str, level: str) -> list:
    """
    Kategoriya va daraja bo'yicha so'zlarni filterlash
    
    words.json'da category yo'qligi sababli,
    so'z ma'nosiga qarab kategoriyalarga ajratamiz
    """
    # Level bo'yicha filterlash
    level_words = [w for w in WORDS if w.get("level") == level]
    
    # Kategoriya keywords
    category_keywords = {
        "family": ["father", "mother", "brother", "sister", "son", "daughter", "parent", "child", "family", "relative", "uncle", "aunt", "grandmother", "grandfather"],
        "home": ["house", "home", "room", "kitchen", "bedroom", "bathroom", "living", "door", "window", "wall", "roof", "floor", "garden"],
        "food": ["food", "eat", "drink", "breakfast", "lunch", "dinner", "bread", "meat", "fish", "fruit", "vegetable", "water", "milk", "tea", "coffee", "rice", "meal"],
        "animals": ["dog", "cat", "bird", "fish", "cow", "horse", "chicken", "animal", "pet", "lion", "tiger", "elephant", "monkey", "bear"],
        "nature": ["tree", "flower", "plant", "forest", "mountain", "river", "sea", "ocean", "lake", "sun", "moon", "star", "cloud", "rain", "snow", "wind", "sky"],
        "time": ["time", "hour", "minute", "second", "day", "week", "month", "year", "morning", "afternoon", "evening", "night", "today", "tomorrow", "yesterday"],
        "colors": ["color", "red", "blue", "green", "yellow", "black", "white", "brown", "pink", "purple", "orange", "grey", "gray"],
        "body": ["body", "head", "eye", "ear", "nose", "mouth", "hand", "arm", "leg", "foot", "finger", "toe", "heart", "brain"],
        "work": ["work", "job", "office", "business", "company", "employee", "manager", "boss", "salary", "career", "professional"],
        "technology": ["computer", "phone", "internet", "email", "website", "software", "technology", "digital", "online", "app", "device"]
    }
    
    keywords = category_keywords.get(category, [])
    
    if not keywords:
        return level_words[:20]  # Default: birinchi 20 ta so'z
    
    # So'z yoki ma'noda keyword bor so'zlarni topish
    filtered = []
    for word in level_words:
        word_text = word.get("word", "").lower()
        meaning_text = word.get("meaning", "").lower()
        
        if any(kw in word_text or kw in meaning_text for kw in keywords):
            filtered.append(word)
    
    return filtered


def register(dp):
    dp.include_router(router)
