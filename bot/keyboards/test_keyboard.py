from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

test_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Ha"), KeyboardButton(text="❌ Yo'q")],
    ],
    resize_keyboard=True
)

test_options = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Test boshlash")],
        [KeyboardButton(text="◀️ Ortga")],
    ],
    resize_keyboard=True
)
