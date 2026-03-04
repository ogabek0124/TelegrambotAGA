import json
from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from keyboards.menus import main_menu
from services.db import get_user_level

router = Router()

# So'zlarni yuklash
with open("data/words.json", "r", encoding="utf-8") as f:
    WORDS = json.load(f)

# Sahifalashtirish holatini saqlash
WORDS_STATE = {}


@router.message(lambda m: m.text == "📘 So'zlar")
async def show_words(message: types.Message):
    """So'zlarni ko'rsatish"""
    user_id = message.from_user.id
    user_level = get_user_level(user_id) or "beginner"

    # Faqat shu levelga mos so'zlar
    level_words = [w for w in WORDS if w.get("level") == user_level]

    if not level_words:
        await message.answer(
            f"❗ {user_level.capitalize()} level uchun so'zlar yo'q",
            reply_markup=main_menu
        )
        return

    # Dastlabki sahifa
    WORDS_STATE[user_id] = {
        "words": level_words,
        "page": 0,
        "level": user_level
    }

    await display_words_page(message, user_id)


async def display_words_page(message: types.Message, user_id: int):
    """Sahifa bo'yicha so'zlarni ko'rsatish"""
    if user_id not in WORDS_STATE:
        return

    state = WORDS_STATE[user_id]
    all_words = state["words"]
    current_page = state["page"]
    level_name = state["level"]

    # Har sahifada 10 so'z
    start_idx = current_page * 10
    end_idx = start_idx + 10
    page_words = all_words[start_idx:end_idx]

    if not page_words:
        state["page"] -= 1
        await display_words_page(message, user_id)
        return

    # Matn yaratish
    total_pages = (len(all_words) + 9) // 10
    msg = f"📘 {level_name.capitalize()} Level\n"
    msg += f"📄 Sahifa {current_page + 1}/{total_pages}\n"
    msg += f"─" * 30 + "\n\n"

    for idx, word in enumerate(page_words, start=start_idx + 1):
        msg += f"{idx}. {word['word']}\n"
        msg += f"   └─ {word['meaning']}\n"

    # Tugmalarni yaratish
    buttons = []

    if current_page > 0:
        buttons.append([KeyboardButton(text="⬅️ Orqaga")])

    if end_idx < len(all_words):
        buttons.append([KeyboardButton(text="➡️ Ko'proq")])

    buttons.append([KeyboardButton(text="🏠 Menu")])

    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    await message.answer(msg, reply_markup=keyboard)


@router.message(lambda m: m.text == "➡️ Ko'proq")
async def next_page(message: types.Message):
    """Keyingi sahifaga o'tish"""
    user_id = message.from_user.id

    if user_id not in WORDS_STATE:
        await message.answer("Avval so'zlarni tanlang!", reply_markup=main_menu)
        return

    WORDS_STATE[user_id]["page"] += 1
    await display_words_page(message, user_id)


@router.message(lambda m: m.text == "⬅️ Orqaga")
async def prev_page(message: types.Message):
    """Oldingi sahifaga o'tish"""
    user_id = message.from_user.id

    if user_id not in WORDS_STATE:
        await message.answer("Avval so'zlarni tanlang!", reply_markup=main_menu)
        return

    if WORDS_STATE[user_id]["page"] > 0:
        WORDS_STATE[user_id]["page"] -= 1
        await display_words_page(message, user_id)


@router.message(lambda m: m.text == "🏠 Menu")
async def back_to_menu(message: types.Message):
    """Asosiy menyuya qaytish"""
    user_id = message.from_user.id

    if user_id in WORDS_STATE:
        del WORDS_STATE[user_id]

    await message.answer("Asosiy menyuga qaytdik", reply_markup=main_menu)


def register(dp):
    dp.include_router(router)
