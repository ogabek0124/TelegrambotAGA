from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎓 Drajani tanlash"), KeyboardButton(text="📚 Kitoblar")],
        [KeyboardButton(text="📘 So'zlar"), KeyboardButton(text="📝 Test")],
        [KeyboardButton(text="📚 Grammar"), KeyboardButton(text="📊 Progress")],
        [KeyboardButton(text="🎥 Videolar"), KeyboardButton(text="🔥 Streakga")],
        [KeyboardButton(text="🏆 Leaderboard")],
    ],
    resize_keyboard=True
)

yes_no_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ha"), KeyboardButton(text="Yo'q")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
