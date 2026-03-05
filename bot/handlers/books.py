"""
Kitoblar (PDF) handler
"""
from pathlib import Path
from aiogram import Router, types
from aiogram.types import FSInputFile
from keyboards.menus import main_menu
from keyboards.books_menu import (
    books_level_menu,
    beginner_books_menu,
    intermediate_books_menu,
    ielts_books_menu
)

router = Router()

# PDF fayllar yo'li
BOOKS_DIR = Path(__file__).resolve().parent.parent / "data" / "books"


# Kitoblar bazasi (fayl nomi va tavsif)
BOOKS = {
    "beginner": {
        "📖 English Grammar in Use (Elementary)": {
            "file": "english_grammar_in_use_elementary.pdf",
            "description": "📚 English Grammar in Use (Elementary)\n\n"
                          "Bu kitob ingliz tili grammatikasini boshlang'ich darajada o'rgatadi. "
                          "Har bir mavzu sodda va tushunarli tilda yozilgan.\n\n"
                          "📖 Darajangiz: Beginner"
        },
        "📖 Essential English Grammar": {
            "file": "essential_english_grammar.pdf",
            "description": "📚 Essential English Grammar\n\n"
                          "Ingliz tilining asosiy grammatika qoidalarini o'rganish uchun juda yaxshi kitob.\n\n"
                          "📖 Darajangiz: Beginner"
        },
        "📖 English for Everyone (Level 1)": {
            "file": "english_for_everyone_level1.pdf",
            "description": "📚 English for Everyone (Level 1)\n\n"
                          "Ushbu kitob vizual rasmlar va oddiy tushuntirishlar bilan to'ldirilgan.\n\n"
                          "📖 Darajangiz: Beginner"
        }
    },
    "intermediate": {
        "📖 English Grammar in Use (Intermediate)": {
            "file": "english_grammar_in_use_intermediate.pdf",
            "description": "📚 English Grammar in Use (Intermediate)\n\n"
                          "O'rta darajadagi o'quvchilar uchun eng mashhur grammatika kitobi.\n\n"
                          "📖 Darajangiz: Intermediate"
        },
        "📖 Oxford Practice Grammar": {
            "file": "oxford_practice_grammar.pdf",
            "description": "📚 Oxford Practice Grammar\n\n"
                          "Oxford noshiri tomonidan chiqarilgan, mashqlar bilan to'ldirilgan kitob.\n\n"
                          "📖 Darajangiz: Intermediate"
        },
        "📖 English for Everyone (Level 3)": {
            "file": "english_for_everyone_level3.pdf",
            "description": "📚 English for Everyone (Level 3)\n\n"
                          "O'rta daraja uchun vizual va interaktiv kitob.\n\n"
                          "📖 Darajangiz: Intermediate"
        }
    },
    "ielts": {
        "📖 Cambridge IELTS 18": {
            "file": "cambridge_ielts_18.pdf",
            "description": "📚 Cambridge IELTS 18\n\n"
                          "IELTS imtihoniga tayyorgarlik ko'rish uchun eng yangi Cambridge resursi.\n\n"
                          "📖 Darajangiz: IELTS"
        },
        "📖 IELTS Trainer": {
            "file": "ielts_trainer.pdf",
            "description": "📚 IELTS Trainer\n\n"
                          "IELTS imtihoni barcha bo'limlari uchun mashqlar va strategiyalar.\n\n"
                          "📖 Darajangiz: IELTS"
        },
        "📖 The Official Guide to IELTS": {
            "file": "official_guide_to_ielts.pdf",
            "description": "📚 The Official Guide to IELTS\n\n"
                          "Rasmiy IELTS tayyorgarlik qo'llanmasi.\n\n"
                          "📖 Darajangiz: IELTS"
        }
    }
}


@router.message(lambda m: m.text and "Kitoblar" in m.text and "📚" in m.text)
async def books_main(message: types.Message):
    """Kitoblar menusi"""
    await message.answer(
        "📚 Ingliz tilini o'rganish uchun kitoblar\n\n"
        "Darajangizni tanlang:",
        reply_markup=books_level_menu
    )


@router.message(lambda m: m.text in ["📗 Beginner Kitoblar", "📙 Intermediate Kitoblar", "📕 IELTS Kitoblar"])
async def show_level_books(message: types.Message):
    """Daraja bo'yicha kitoblar ro'yxati"""
    if "Beginner" in message.text:
        await message.answer(
            "📗 Beginner daraja uchun kitoblar:",
            reply_markup=beginner_books_menu
        )
    elif "Intermediate" in message.text:
        await message.answer(
            "📙 Intermediate daraja uchun kitoblar:",
            reply_markup=intermediate_books_menu
        )
    elif "IELTS" in message.text:
        await message.answer(
            "📕 IELTS daraja uchun kitoblar:",
            reply_markup=ielts_books_menu
        )


@router.message(lambda m: m.text and m.text.startswith("📖 "))
async def send_book(message: types.Message):
    """PDF kitobni yuborish"""
    book_name = message.text
    
    # Qaysi darajadan ekanligini aniqlash
    level = None
    book_info = None
    
    for lvl in ["beginner", "intermediate", "ielts"]:
        if book_name in BOOKS[lvl]:
            level = lvl
            book_info = BOOKS[lvl][book_name]
            break
    
    if not book_info:
        await message.answer(
            "❌ Kitob topilmadi",
            reply_markup=main_menu
        )
        return
    
    # PDF fayl yo'li
    file_path = BOOKS_DIR / book_info["file"]
    
    if not file_path.exists():
        await message.answer(
            f"❌ Kitob fayli topilmadi.\n\n"
            f"📋 Quyida kitob haqida ma'lumot:\n\n"
            f"{book_info['description']}\n\n"
            f"💡 Eslatma: PDF faylni qo'shish uchun admin bilan bog'laning.",
            reply_markup=books_level_menu
        )
        return
    
    try:
        # PDF faylni yuborish
        await message.answer("📤 Kitobni yuborish boshlandi...")
        
        document = FSInputFile(file_path)
        await message.answer_document(
            document=document,
            caption=book_info["description"]
        )
        
        await message.answer(
            "✅ Kitob muvaffaqiyatli yuborildi!\n\n"
            "📚 Boshqa kitoblar kerakmi?",
            reply_markup=books_level_menu
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Xatolik yuz berdi: {e}\n\n"
            "Iltimos, qaytadan urinib ko'ring yoki admin bilan bog'laning.",
            reply_markup=books_level_menu
        )


@router.message(lambda m: m.text == "◀️ Ortga" and "books" in str(m))
async def back_to_main(message: types.Message):
    """Asosiy menyuga qaytish"""
    await message.answer("🏠 Asosiy menu", reply_markup=main_menu)


def register(dp):
    dp.include_router(router)
