import json
import random
from pathlib import Path
from aiogram import Router, types
from keyboards.menus import main_menu
from services.db import get_connection, get_today

router = Router()

# So'zlar va grammar yuklash
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

try:
    with open(DATA_DIR / "words.json", "r", encoding="utf-8") as f:
        WORDS = json.load(f)
except:
    WORDS = []

try:
    with open(DATA_DIR / "grammar.json", "r", encoding="utf-8") as f:
        GRAMMAR = json.load(f)
except:
    GRAMMAR = []


def is_daily_learned(user_id: int):
    """Bugun o'qilganmi tekshirish"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT learned_date FROM daily_lessons WHERE user_id=?", (user_id,))
            row = c.fetchone()
            if row and row[0] == get_today():
                return True
    except:
        pass
    return False


def mark_daily_learned(user_id: int):
    """Bugun o'qigan marklab qo'yish"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
            INSERT INTO daily_lessons (user_id, learned_date)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET learned_date=?
            """, (user_id, get_today(), get_today()))
            conn.commit()
    except Exception as e:
        print(f"Daily mark error: {e}")


def get_daily_content(user_id: int):
    """Bugun uchun so'z va grammar olish"""
    try:
        # Random seed shu kunning uchun bir xil bo'ladi
        today_str = get_today()
        seed = int(today_str.replace("-", "")) + user_id
        random.seed(seed)
        
        # Random so'z
        if not WORDS:
            return None
        word = random.choice(WORDS)
        
        # User level'ga mos grammar
        level = "beginner"
        try:
            with get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT level FROM progress WHERE user_id=?", (user_id,))
                row = c.fetchone()
                if row and row[0]:
                    level = row[0]
        except:
            pass
        
        # Level ga mos grammar tanlash
        level_grammar = [g for g in GRAMMAR if g.get("level") == level]
        if not level_grammar:
            level_grammar = GRAMMAR
        
        if not level_grammar:
            return None
            
        grammar = random.choice(level_grammar)
        
        return {
            "word": word,
            "grammar": grammar
        }
    except Exception as e:
        print(f"Daily content error: {e}")
        return None


@router.message(lambda m: m.text and "Bugun darsga" in m.text)
async def daily_lesson(message: types.Message):
    try:
        user_id = message.from_user.id
        
        # Tekshirish: bugun o'qilganmi?
        if is_daily_learned(user_id):
            await message.answer(
                "Siz bugun darsni allaqachon o'qidingiz!\n"
                "Ertaga yana dars bo'ladi!",
                reply_markup=main_menu
            )
            return
        
        content = get_daily_content(user_id)
        
        if not content:
            await message.answer(
                "Dars ma'lumotini yuklashda xato. Iltimos qayta urinib ko'ring.",
                reply_markup=main_menu
            )
            return
        
        word = content["word"]
        grammar = content["grammar"]
        
        # Bugun o'qigan marklab qo'yish
        mark_daily_learned(user_id)
        
        text = (
            f"BUGUNNING DARSGA\n\n"
            f"📘 SO'Z:\n"
            f"{word['word']} - {word['meaning']}\n\n"
            f"📚 GRAMMAR:\n"
            f"{grammar['title']}\n"
            f"Qoida: {grammar['rule']}\n"
            f"Misol: {grammar['example']}\n\n"
            f"Tabriklaymiz! Dars yakunlandi!"
        )
        
        await message.answer(text, reply_markup=main_menu)
        
    except Exception as e:
        print(f"Daily lesson error: {e}")
        await message.answer(
            "Xatolik yuz berdi. Iltimos qayta urinib ko'ring.",
            reply_markup=main_menu
        )


def register(dp):
    dp.include_router(router)
