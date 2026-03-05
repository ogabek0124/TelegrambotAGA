"""
Achievements & Badges - yutuqlar tizimi
"""
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

try:
    import psycopg2
    USE_POSTGRES = bool(os.getenv("DATABASE_URL"))
except ImportError:
    USE_POSTGRES = False

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Database connection"""
    if USE_POSTGRES and DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        return sqlite3.connect("data/progress.db")


# Yutuqlar ro'yxati
ACHIEVEMENTS = {
    "first_test": {
        "id": "first_test",
        "title": "🎯 Birinchi Test",
        "description": "Birinchi testni tugatdingiz!",
        "icon": "🎯",
        "points": 10
    },
    "perfect_score": {
        "id": "perfect_score",
        "title": "💯 Perfect Score",
        "description": "100% to'g'ri javob berdingiz!",
        "icon": "💯",
        "points": 50
    },
    "speed_demon": {
        "id": "speed_demon",
        "title": "⚡ Speed Demon",
        "description": "Testni 5 daqiqadan tez tugatdingiz!",
        "icon": "⚡",
        "points": 30
    },
    "streak_7": {
        "id": "streak_7",
        "title": "🔥 7 Kunlik Streak",
        "description": "7 kun ketma-ket test yechdingiz!",
        "icon": "🔥",
        "points": 40
    },
    "streak_30": {
        "id": "streak_30",
        "title": "🏅 30 Kunlik Champion",
        "description": "30 kun ketma-ket test yechdingiz!",
        "icon": "🏅",
        "points": 100
    },
    "word_master": {
        "id": "word_master",
        "title": "📚 Word Master",
        "description": "100 ta so'z o'rgandingiz!",
        "icon": "📚",
        "points": 60
    },
    "grammar_guru": {
        "id": "grammar_guru",
        "title": "📖 Grammar Guru",
        "description": "Barcha grammar qoidalarni o'rgandingiz!",
        "icon": "📖",
        "points": 80
    },
    "test_veteran": {
        "id": "test_veteran",
        "title": "🎓 Test Veteran",
        "description": "50 ta test yechdingiz!",
        "icon": "🎓",
        "points": 100
    },
    "early_bird": {
        "id": "early_bird",
        "title": "🌅 Early Bird",
        "description": "Ertalab soat 6 da test yechdingiz!",
        "icon": "🌅",
        "points": 20
    },
    "night_owl": {
        "id": "night_owl",
        "title": "🦉 Night Owl",
        "description": "Tunda soat 23 dan keyin test yechdingiz!",
        "icon": "🦉",
        "points": 20
    }
}


def init_achievements_table():
    """Yutuqlar jadvalini yaratish"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                achievement_id VARCHAR(50) NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, achievement_id)
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_id TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, achievement_id)
            )
        """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ user_achievements jadvali yaratildi")


def award_achievement(user_id: int, achievement_id: str):
    """Yutuq berish"""
    if achievement_id not in ACHIEVEMENTS:
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholder = "%s" if USE_POSTGRES else "?"
    
    try:
        query = f"""
            INSERT INTO user_achievements (user_id, achievement_id)
            VALUES ({placeholder}, {placeholder})
        """
        cursor.execute(query, (user_id, achievement_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except:
        cursor.close()
        conn.close()
        return False  # Already has this achievement


def get_user_achievements(user_id: int):
    """Foydalanuvchi yutuqlarini olish"""
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholder = "%s" if USE_POSTGRES else "?"
    
    query = f"""
        SELECT achievement_id, earned_at
        FROM user_achievements
        WHERE user_id = {placeholder}
        ORDER BY earned_at DESC
    """
    
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results


def get_achievement_progress(user_id: int):
    """Yutuqlar progressi"""
    earned = get_user_achievements(user_id)
    earned_ids = [ach[0] for ach in earned]
    
    total_achievements = len(ACHIEVEMENTS)
    earned_count = len(earned_ids)
    
    total_points = sum(ach["points"] for ach in ACHIEVEMENTS.values())
    earned_points = sum(ACHIEVEMENTS[ach_id]["points"] for ach_id in earned_ids if ach_id in ACHIEVEMENTS)
    
    return {
        "total_achievements": total_achievements,
        "earned_achievements": earned_count,
        "total_points": total_points,
        "earned_points": earned_points,
        "percentage": (earned_count / total_achievements * 100) if total_achievements > 0 else 0
    }


def check_and_award_achievements(user_id: int, test_data: dict):
    """Test natijasiga qarab yutuqlarni tekshirish va berish"""
    awarded = []
    
    # First Test
    from services.test_history import get_test_history
    history = get_test_history(user_id, limit=1)
    if len(history) == 1:
        if award_achievement(user_id, "first_test"):
            awarded.append("first_test")
    
    # Perfect Score
    if test_data.get("correct") == test_data.get("total") and test_data.get("total") > 0:
        if award_achievement(user_id, "perfect_score"):
            awarded.append("perfect_score")
    
    # Speed Demon
    if test_data.get("time_spent") and test_data.get("time_spent") < 300:  # 5 minutes
        if award_achievement(user_id, "speed_demon"):
            awarded.append("speed_demon")
    
    # Streak achievements
    from services.db import get_streak
    streak = get_streak(user_id)
    
    if streak >= 7:
        if award_achievement(user_id, "streak_7"):
            awarded.append("streak_7")
    
    if streak >= 30:
        if award_achievement(user_id, "streak_30"):
            awarded.append("streak_30")
    
    # Test Veteran
    all_history = get_test_history(user_id, limit=100)
    if len(all_history) >= 50:
        if award_achievement(user_id, "test_veteran"):
            awarded.append("test_veteran")
    
    # Time-based achievements
    from datetime import datetime
    current_hour = datetime.now().hour
    
    if current_hour >= 5 and current_hour < 7:
        if award_achievement(user_id, "early_bird"):
            awarded.append("early_bird")
    
    if current_hour >= 23 or current_hour < 2:
        if award_achievement(user_id, "night_owl"):
            awarded.append("night_owl")
    
    return awarded


if __name__ == "__main__":
    init_achievements_table()
