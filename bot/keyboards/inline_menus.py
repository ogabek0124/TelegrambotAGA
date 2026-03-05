"""
Inline keyboards - chiroyliroq va qulay UI uchun
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_inline():
    """Asosiy menyu inline"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎓 Daraja", callback_data="menu:level"),
            InlineKeyboardButton(text="📚 Kitoblar", callback_data="menu:books")
        ],
        [
            InlineKeyboardButton(text="📘 So'zlar", callback_data="menu:words"),
            InlineKeyboardButton(text="📝 Test", callback_data="menu:test")
        ],
        [
            InlineKeyboardButton(text="📚 Grammar", callback_data="menu:grammar"),
            InlineKeyboardButton(text="📊 Progress", callback_data="menu:progress")
        ],
        [
            InlineKeyboardButton(text="🎥 Videolar", callback_data="menu:videos"),
            InlineKeyboardButton(text="🔥 Streak", callback_data="menu:streak")
        ],
        [
            InlineKeyboardButton(text="🏆 Leaderboard", callback_data="menu:leaderboard"),
            InlineKeyboardButton(text="🎖 Yutuqlar", callback_data="menu:achievements")
        ]
    ])


def get_level_menu_inline():
    """Daraja tanlash inline"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Beginner", callback_data="level:beginner")],
        [InlineKeyboardButton(text="🟡 Intermediate", callback_data="level:intermediate")],
        [InlineKeyboardButton(text="🔴 IELTS", callback_data="level:ielts")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
    ])


def get_words_menu_inline():
    """So'zlar menyu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📖 Barcha so'zlar", callback_data="words:all"),
            InlineKeyboardButton(text="🔍 Qidirish", callback_data="words:search")
        ],
        [
            InlineKeyboardButton(text="🗂 Kategoriyalar", callback_data="words:categories"),
            InlineKeyboardButton(text="💾 Flashcard", callback_data="words:flashcard")
        ],
        [
            InlineKeyboardButton(text="⭐ Sevimlilar", callback_data="words:favorites"),
            InlineKeyboardButton(text="🎲 Tasodifiy", callback_data="words:random")
        ],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
    ])


def get_test_menu_inline():
    """Test menyu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Vocabulary Test", callback_data="test:vocabulary"),
            InlineKeyboardButton(text="📚 Grammar Test", callback_data="test:grammar")
        ],
        [
            InlineKeyboardButton(text="🎯 Qiyinlik: Oson", callback_data="test:easy"),
            InlineKeyboardButton(text="🎯 Qiyinlik: Qiyin", callback_data="test:hard")
        ],
        [
            InlineKeyboardButton(text="📊 Natijalar tarixi", callback_data="test:history")
        ],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
    ])


def get_grammar_menu_inline(page=0, total_pages=1):
    """Grammar menyu"""
    keyboard = [
        [
            InlineKeyboardButton(text="📖 Barcha qoidalar", callback_data="grammar:all"),
            InlineKeyboardButton(text="💪 Mashqlar", callback_data="grammar:practice")
        ],
        [
            InlineKeyboardButton(text="🟢 Beginner", callback_data="grammar:beginner"),
            InlineKeyboardButton(text="🟡 Intermediate", callback_data="grammar:intermediate")
        ],
        [
            InlineKeyboardButton(text="🔴 IELTS", callback_data="grammar:ielts")
        ]
    ]
    
    # Pagination
    if total_pages > 1:
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"grammar:page:{page-1}"))
        nav_row.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="grammar:page:current"))
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"grammar:page:{page+1}"))
        keyboard.append(nav_row)
    
    keyboard.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_books_level_menu_inline():
    """Kitoblar daraja tanlash"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📗 Beginner Kitoblar", callback_data="books:beginner")],
        [InlineKeyboardButton(text="📙 Intermediate Kitoblar", callback_data="books:intermediate")],
        [InlineKeyboardButton(text="📕 IELTS Kitoblar", callback_data="books:ielts")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")]
    ])


def get_back_button(callback_data="back:main"):
    """Oddiy ortga tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Ortga", callback_data=callback_data)]
    ])


def get_pagination_keyboard(current_page, total_pages, prefix):
    """Universal pagination keyboard"""
    keyboard = []
    
    nav_row = []
    if current_page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"{prefix}:page:{current_page-1}"))
    
    nav_row.append(InlineKeyboardButton(text=f"📄 {current_page+1}/{total_pages}", callback_data=f"{prefix}:page:current"))
    
    if current_page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"{prefix}:page:{current_page+1}"))
    
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="back:main")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_word_categories_inline():
    """So'z kategoriyalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👨‍👩‍👧 Family", callback_data="category:family"),
            InlineKeyboardButton(text="🏠 Home", callback_data="category:home")
        ],
        [
            InlineKeyboardButton(text="🍔 Food", callback_data="category:food"),
            InlineKeyboardButton(text="🐕 Animals", callback_data="category:animals")
        ],
        [
            InlineKeyboardButton(text="🌳 Nature", callback_data="category:nature"),
            InlineKeyboardButton(text="⏰ Time", callback_data="category:time")
        ],
        [
            InlineKeyboardButton(text="🎨 Colors", callback_data="category:colors"),
            InlineKeyboardButton(text="👤 Body", callback_data="category:body")
        ],
        [
            InlineKeyboardButton(text="💼 Work", callback_data="category:work"),
            InlineKeyboardButton(text="📱 Technology", callback_data="category:technology")
        ],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="menu:words")]
    ])


def get_test_answer_keyboard(options, correct_index):
    """Test javoblari uchun inline keyboard"""
    keyboard = []
    
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(
            text=f"{chr(65+i)}) {option}",
            callback_data=f"answer:{i}:{correct_index}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="🛑 To'xtatish", callback_data="test:stop")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_flashcard_keyboard(word_id, total_words, current_index):
    """Flashcard uchun keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Javobni ko'rish", callback_data=f"flashcard:reveal:{word_id}")],
        [
            InlineKeyboardButton(text="😊 Bildim", callback_data=f"flashcard:known:{word_id}"),
            InlineKeyboardButton(text="🤔 Bilmayman", callback_data=f"flashcard:unknown:{word_id}")
        ],
        [
            InlineKeyboardButton(text="⭐ Sevimli", callback_data=f"flashcard:fav:{word_id}"),
            InlineKeyboardButton(text=f"📊 {current_index+1}/{total_words}", callback_data="flashcard:stats")
        ],
        [
            InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"flashcard:prev:{current_index}"),
            InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"flashcard:next:{current_index}")
        ],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="menu:words")]
    ])
