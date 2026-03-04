from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def video_categories_menu():
    """Video kategoriyalari"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📻 Tinglash"), KeyboardButton(text="🎤 Talaffuz")],
            [KeyboardButton(text="✏️ Grammatika Videolar"), KeyboardButton(text="📚 So'z Videolar")],
            [KeyboardButton(text="⬅️ Orqaga")],
        ],
        resize_keyboard=True
    )


def video_list_menu(category: str, count: int):
    """Videolar ro'yxati - creates buttons for each video in category"""
    buttons = []
    
    # Add video buttons
    for i in range(1, count + 1):
        buttons.append(KeyboardButton(text=f"📺 Video_{category}_{i}"))
    
    # Create keyboard layout - 2 buttons per row
    keyboard = []
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            # Two buttons in this row
            keyboard.append([buttons[i], buttons[i + 1]])
        else:
            # Only one button in this row
            keyboard.append([buttons[i]])
    
    # Add back button on separate row
    keyboard.append([KeyboardButton(text="⬅️ Orqaga")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
