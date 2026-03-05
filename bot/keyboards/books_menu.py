"""
Kitoblar (PDF) menusi keyboards
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Daraja tanlash uchun
books_level_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📗 Beginner Kitoblar")],
        [KeyboardButton(text="📙 Intermediate Kitoblar")],
        [KeyboardButton(text="📕 IELTS Kitoblar")],
        [KeyboardButton(text="◀️ Ortga")],
    ],
    resize_keyboard=True
)


# Beginner kitoblar
beginner_books_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 English Grammar in Use (Elementary)")],
        [KeyboardButton(text="📖 Essential English Grammar")],
        [KeyboardButton(text="📖 English for Everyone (Level 1)")],
        [KeyboardButton(text="◀️ Ortga")],
    ],
    resize_keyboard=True
)


# Intermediate kitoblar
intermediate_books_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 English Grammar in Use (Intermediate)")],
        [KeyboardButton(text="📖 Oxford Practice Grammar")],
        [KeyboardButton(text="📖 English for Everyone (Level 3)")],
        [KeyboardButton(text="◀️ Ortga")],
    ],
    resize_keyboard=True
)


# IELTS kitoblar
ielts_books_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 Cambridge IELTS 18")],
        [KeyboardButton(text="📖 IELTS Trainer")],
        [KeyboardButton(text="📖 The Official Guide to IELTS")],
        [KeyboardButton(text="◀️ Ortga")],
    ],
    resize_keyboard=True
)
