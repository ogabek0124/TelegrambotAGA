"""
Grammar Test - grammatika qoidalar bo'yicha test
"""
import json
import random
import time
from pathlib import Path
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.db import get_user_level
from services.test_history import save_test_result

router = Router()

# Grammar ma'lumotlari
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
with open(DATA_DIR / "grammar.json", "r", encoding="utf-8") as f:
    GRAMMAR = json.load(f)

# Test holati
GRAMMAR_TEST_STATE = {}


def create_grammar_question(grammar_rule):
    """Grammar qoidadan savol yaratish"""
    # Misol jumlalardan birini tanlaymiz
    examples = grammar_rule.get("examples", [])
    if not examples:
        return None
    
    example = random.choice(examples)
    
    # Javob - to'g'ri jumla
    correct_answer = example["english"]
    
    # Noto'g'ri variantlar - xato misollardan
    wrong_answers = []
    common_mistakes = grammar_rule.get("common_mistakes", [])
    
    for mistake in common_mistakes[:3]:
        wrong_answers.append(mistake.get("wrong", ""))
    
    # Agar yetarli noto'g'ri javob bo'lmasa, boshqa grammar'dan olamos
    while len(wrong_answers) < 3:
        other_grammar = random.choice(GRAMMAR)
        if other_grammar.get("id") != grammar_rule.get("id"):
            other_examples = other_grammar.get("examples", [])
            if other_examples:
                wrong_answers.append(random.choice(other_examples)["english"])
    
    wrong_answers = wrong_answers[:3]
    
    # Savolni qaytaramiz
    return {
        "question": f"Qaysi jumla to'g'ri?\n\n📖 Qoida: {grammar_rule['title']}",
        "correct": correct_answer,
        "options": [correct_answer] + wrong_answers,
        "explanation": example.get("note", "")
    }


@router.callback_query(F.data == "test:grammar")
async def start_grammar_test(callback: CallbackQuery):
    """Grammar test boshlash"""
    user_id = callback.from_user.id
    user_level = get_user_level(user_id) or "beginner"
    
    # Foydalanuvchi darajasiga mos grammar qoidalar
    level_grammar = [g for g in GRAMMAR if g.get("level") == user_level]
    
    if not level_grammar:
        await callback.answer("❌ Bu daraja uchun grammar qoidalar yo'q", show_alert=True)
        return
    
    # 10 ta savol yaratamiz
    questions = []
    for _ in range(min(10, len(level_grammar))):
        grammar_rule = random.choice(level_grammar)
        question = create_grammar_question(grammar_rule)
        if question:
            random.shuffle(question["options"])
            questions.append(question)
    
    if not questions:
        await callback.answer("❌ Savollar yaratishda xato", show_alert=True)
        return
    
    # Holatni saqlaymiz
    GRAMMAR_TEST_STATE[user_id] = {
        "questions": questions,
        "current": 0,
        "correct": 0,
        "start_time": time.time()
    }
    
    await show_grammar_question(callback, user_id)
    await callback.answer("📝 Grammar Test boshlandi!")


async def show_grammar_question(callback: CallbackQuery, user_id: int):
    """Grammar savol ko'rsatish"""
    if user_id not in GRAMMAR_TEST_STATE:
        return
    
    state = GRAMMAR_TEST_STATE[user_id]
    current = state["current"]
    questions = state["questions"]
    
    if current >= len(questions):
        # Test tugadi
        correct = state["correct"]
        total = len(questions)
        time_spent = int(time.time() - state["start_time"])
        percentage = (correct / total) * 100
        
        # Natijani saqlash
        save_test_result(
            user_id=user_id,
            test_type="grammar",
            correct=correct,
            total=total,
            difficulty="medium",
            time_spent=time_spent
        )
        
        await callback.message.edit_text(
            f"📝 <b>Grammar Test Tugadi!</b>\n\n"
            f"✅ To'g'ri: {correct}/{total}\n"
            f"📈 Foiz: {percentage:.1f}%\n"
            f"⏱ Vaqt: {time_spent // 60}:{time_spent % 60:02d}\n\n"
            f"{'🎉 A+oyib!' if percentage >= 80 else '💪 Davom eting!'}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
            ])
        )
        
        del GRAMMAR_TEST_STATE[user_id]
        return
    
    question_data = questions[current]
    
    # Inline keyboard yaratish
    keyboard = []
    for i, option in enumerate(question_data["options"]):
        # Correct indexni topamiz
        correct_index = question_data["options"].index(question_data["correct"])
        keyboard.append([InlineKeyboardButton(
            text=f"{chr(65+i)}) {option[:40]}...",
            callback_data=f"grammar_ans:{i}:{correct_index}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="🛑 To'xtatish", callback_data="grammar_stop")])
    
    await callback.message.edit_text(
        f"📝 <b>Savol {current + 1}/{len(questions)}</b>\n\n"
        f"{question_data['question']}\n\n"
        f"Tog'ri javobni tanlang:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )


@router.callback_query(F.data.startswith("grammar_ans:"))
async def handle_grammar_answer(callback: CallbackQuery):
    """Grammar javobni tekshirish"""
    user_id = callback.from_user.id
    
    if user_id not in GRAMMAR_TEST_STATE:
        await callback.answer("❌ Test topilmadi", show_alert=True)
        return
    
    # Javobni parse qilish
    _, selected, correct = callback.data.split(":")
    selected = int(selected)
    correct = int(correct)
    
    state = GRAMMAR_TEST_STATE[user_id]
    question_data = state["questions"][state["current"]]
    
    if selected == correct:
        state["correct"] += 1
        feedback = "✅ To'g'ri!"
    else:
        feedback = f"❌ Noto'g'ri!\n\n✅ To'g'ri javob: {question_data['correct']}"
        if question_data.get("explanation"):
            feedback += f"\n\n💡 {question_data['explanation']}"
    
    state["current"] += 1
    
    await callback.answer(feedback, show_alert=True)
    await show_grammar_question(callback, user_id)


@router.callback_query(F.data == "grammar_stop")
async def stop_grammar_test(callback: CallbackQuery):
    """Grammar testni to'xtatish"""
    user_id = callback.from_user.id
    
    if user_id in GRAMMAR_TEST_STATE:
        del GRAMMAR_TEST_STATE[user_id]
    
    await callback.message.edit_text(
        "🛑 Test to'xtatildi",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
        ])
    )
    await callback.answer()


def register(dp):
    dp.include_router(router)
