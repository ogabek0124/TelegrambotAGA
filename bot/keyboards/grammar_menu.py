from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

grammar_menu = ReplyKeyboardMarkup(
    keyboard=[
        # Beginner
        [KeyboardButton(text="1️⃣ Present Simple"), KeyboardButton(text="2️⃣ Past Simple")],
        [KeyboardButton(text="3️⃣ Present Continuous"), KeyboardButton(text="4️⃣ Will (Future)")],
        # Intermediate
        [KeyboardButton(text="5️⃣ Present Perfect"), KeyboardButton(text="6️⃣ Present Perfect Cont.")],
        [KeyboardButton(text="7️⃣ Passive Voice"), KeyboardButton(text="8️⃣ Conditional")],
        # IELTS
        [KeyboardButton(text="9️⃣ Reported Speech"), KeyboardButton(text="🔟 Inversion")],
        [KeyboardButton(text="◀️ Ortga")],
    ],
    resize_keyboard=True
)
