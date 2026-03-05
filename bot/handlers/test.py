import json
import random
from pathlib import Path
from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from keyboards.menus import main_menu
from services.db import get_user_level
from services.user_sync import update_user_progress
import sqlite3

router = Router()

# Test holatini saqlash
ACTIVE_TESTS = {}

# So'zlarni yuklash
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

with open(DATA_DIR / "words.json", "r", encoding="utf-8") as f:
    WORDS = json.load(f)


def create_continue_keyboard():
    """Davom etish tugmasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Keyingi savol")],
            [KeyboardButton(text="Testni to'xtatish")],
        ],
        resize_keyboard=True
    )


def save_test_result(user_id: int, correct: int, total: int, level: str = None):
    """Test natijasini saqlash va Django admin'ga sync qilish"""
    from services.db import get_connection, update_streak, get_today, get_streak
    
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO progress (user_id, correct, total, last_date)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            correct=?,
            total=?,
            last_date=?
        """, (user_id, correct, total, get_today(), correct, total, get_today()))
        conn.commit()
    
    # Streak'ni yangilash
    update_streak(user_id)
    streak = get_streak(user_id)
    
    # Django admin'ga sync qilish
    update_user_progress(
        telegram_id=user_id,
        correct=correct,
        total=total,
        streak=streak,
        level=level
    )


def create_options_keyboard(options):
    """Test variantlari uchun keyboard yaratish"""
    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([KeyboardButton(text=f"{chr(65+i)}) {option}")])
    
    keyboard.append([KeyboardButton(text="Testni to'xtatish")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


@router.message(lambda m: m.text and "Test" in m.text)
async def start_test(message: types.Message):
    user_id = message.from_user.id

    # User levelni olamiz
    user_level = get_user_level(user_id) or "beginner"

    # Faqat shu levelga mos so'zlar
    level_words = [w for w in WORDS if w.get("level") == user_level]

    if not level_words:
        await message.answer(
            "Bu level uchun so'zlar yo'q",
            reply_markup=main_menu
        )
        return

    if len(level_words) < 4:
        await message.answer(
            f"Test uchun minimal 4 ta so'z kerak (hozir {len(level_words)} ta bor)",
            reply_markup=main_menu
        )
        return

    # 20 ta savol yoki mavjud so'zlarning barchasi
    num_questions = min(20, len(level_words))
    questions = random.sample(level_words, num_questions)

    # Test holatini saqlaymiz
    ACTIVE_TESTS[user_id] = {
        "questions": questions,
        "current": 0,
        "correct": 0,
        "answered": 0,
        "level": user_level,
        "waiting_answer": True
    }

    await show_question(message, user_id)


async def show_question(message: types.Message, user_id: int):
    if user_id not in ACTIVE_TESTS:
        return

    test_data = ACTIVE_TESTS[user_id]
    current_idx = test_data["current"]
    questions = test_data["questions"]

    if current_idx >= len(questions):
        # Test tugadi
        correct = test_data["correct"]
        total = len(questions)
        percentage = (correct / total) * 100
        level = test_data.get("level", "beginner")

        save_test_result(user_id, correct, total, level)

        await message.answer(
            f"Test tugadi!\n\n"
            f"To'g'ri javoblar: {correct}/{total}\n"
            f"Foiz: {percentage:.1f}%",
            reply_markup=main_menu
        )

        del ACTIVE_TESTS[user_id]
        return

    question = questions[current_idx]
    
    # Variantlarni yaratish
    # To'g'ri javob = shuning ma'nosi
    correct_answer = question['meaning']
    
    # Noto'g'ri javoblar - boshqa so'zlarning ma'nolari
    other_meanings = [w['meaning'] for w in questions if w['word'] != question['word']]
    
    # Agar yetarli noto'g'ri javob yo'lmasa, to'g'ri javobni takrorlash
    if len(other_meanings) < 3:
        other_meanings = [w['meaning'] for w in WORDS if w['meaning'] != correct_answer][:3]
    
    wrong_answers = random.sample(other_meanings, min(3, len(other_meanings)))
    
    # Variantlar aralashi
    options = [correct_answer] + wrong_answers
    random.shuffle(options)
    
    # Correct answer indexini saqlash
    correct_index = options.index(correct_answer)
    test_data['correct_index'] = correct_index
    test_data['waiting_answer'] = True
    
    # Savol
    text = (
        f"Savol {current_idx + 1}/{len(questions)}\n\n"
        f"'{question['word']}' ning ma'nosi nima?\n"
    )
    
    keyboard = create_options_keyboard(options)
    
    await message.answer(text, reply_markup=keyboard)


@router.message(lambda m: m.text.startswith("A) ") or m.text.startswith("B) ") or m.text.startswith("C) ") or m.text.startswith("D) "))
async def handle_answer(message: types.Message):
    user_id = message.from_user.id

    if user_id not in ACTIVE_TESTS:
        await message.answer("Test boshlang!", reply_markup=main_menu)
        return

    test_data = ACTIVE_TESTS[user_id]
    
    if not test_data.get('waiting_answer'):
        return
    
    # Javob index'ini olish
    answer_letter = message.text[0]  # A, B, C yoki D
    answer_index = ord(answer_letter) - ord('A')  # 0, 1, 2 yoki 3
    
    # To'g'ri javobni tekshirish
    questions = test_data["questions"]
    correct_question = questions[test_data["current"]]
    correct_answer = correct_question['meaning']
    
    if answer_index == test_data['correct_index']:
        test_data["correct"] += 1
        feedback = f"To'g'ri javob: {correct_answer}"
    else:
        # Noto'g'ri bo'lsa, to'g'ri javobni ko'rsatish
        feedback = f"Noto'g'ri!\n\nTo'g'ri javob: {correct_answer}"

    # Javob berilgan savollar soni (to'g'ri yoki noto'g'ri bo'lishidan qat'i nazar)
    test_data["answered"] += 1
    
    test_data['waiting_answer'] = False
    
    await message.answer(feedback, reply_markup=create_continue_keyboard())


@router.message(lambda m: m.text and "Keyingi savol" in m.text)
async def next_question(message: types.Message):
    user_id = message.from_user.id

    if user_id not in ACTIVE_TESTS:
        await message.answer("Test boshlang!", reply_markup=main_menu)
        return

    test_data = ACTIVE_TESTS[user_id]
    test_data["current"] += 1
    
    await show_question(message, user_id)


@router.message(lambda m: m.text and "Testni to" in m.text)
async def stop_test(message: types.Message):
    user_id = message.from_user.id

    if user_id in ACTIVE_TESTS:
        test_data = ACTIVE_TESTS[user_id]
        correct = test_data["correct"]
        answered = test_data.get("answered", 0)

        if answered > 0:
            percentage = (correct / answered) * 100
            await message.answer(
                f"Test to'xtadi!\n\n"
                f"To'g'ri javoblar: {correct}/{answered}\n"
                f"Foiz: {percentage:.1f}%",
                reply_markup=main_menu
            )
        else:
            await message.answer("Test boshlash uchun vaqt yo'q", reply_markup=main_menu)
        
        del ACTIVE_TESTS[user_id]
    else:
        await message.answer("Hozir test davom etmayapti", reply_markup=main_menu)


def register(dp):
    dp.include_router(router)
