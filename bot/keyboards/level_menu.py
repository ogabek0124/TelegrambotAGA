from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

level_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🟢 Beginner")],
        [KeyboardButton(text="🟡 Intermediate")],
        [KeyboardButton(text="🔴 IELTS")],
        [KeyboardButton(text="◀️ Ortga")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
