from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

test_options = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="A)"), KeyboardButton(text="B)"), KeyboardButton(text="C)"), KeyboardButton(text="D)")],
    ],
    resize_keyboard=True
)
