"""
Telegram user'larni Django admin'ga sync qilish uchun yordamchi funksiyalar
"""
import asyncio
import os
from datetime import date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if PostgreSQL is available
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_POSTGRES = bool(os.getenv("DATABASE_URL"))
except ImportError:
    USE_POSTGRES = False

DATABASE_URL = os.getenv("DATABASE_URL")


def sync_telegram_user(telegram_id: int, username: str = None, first_name: str = None):
    """
    Telegram foydalanuvchini Django admin'ga sync qilish
    
    Args:
        telegram_id: Telegram user ID
        username: Telegram username (@username)
        first_name: Telegram first name
    """
    if not USE_POSTGRES or not DATABASE_URL:
        # SQLite rejimida - sync qilish mumkin emas
        return False
    
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=3)
        cursor = conn.cursor()
        
        # Check if user exists in Django's api_telegramuser table
        cursor.execute("""
            SELECT id FROM api_telegramuser WHERE telegram_id = %s
        """, (telegram_id,))
        
        exists = cursor.fetchone()
        
        if exists:
            # Update existing user
            cursor.execute("""
                UPDATE api_telegramuser 
                SET username = %s, first_name = %s, updated_at = NOW()
                WHERE telegram_id = %s
            """, (username, first_name, telegram_id))
        else:
            # Insert new user
            cursor.execute("""
                INSERT INTO api_telegramuser 
                (telegram_id, username, first_name, correct, total, streak, level, created_at, updated_at)
                VALUES (%s, %s, %s, 0, 0, 0, 'beginner', NOW(), NOW())
            """, (telegram_id, username, first_name))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ User sync error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_user_progress(telegram_id: int, correct: int = None, total: int = None, 
                         streak: int = None, level: str = None):
    """
    Foydalanuvchi progressini Django admin'ga sync qilish
    
    Args:
        telegram_id: Telegram user ID
        correct: To'g'ri javoblar soni
        total: Jami javoblar
        streak: Ketma-ket kunlar
        level: Daraja (beginner/intermediate/ielts)
    """
    if not USE_POSTGRES or not DATABASE_URL:
        return False
    
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=3)
        cursor = conn.cursor()
        
        # Build UPDATE query dynamically
        update_fields = []
        values = []
        
        if correct is not None:
            update_fields.append("correct = %s")
            values.append(correct)
        
        if total is not None:
            update_fields.append("total = %s")
            values.append(total)
        
        if streak is not None:
            update_fields.append("streak = %s")
            values.append(streak)
        
        if level is not None:
            update_fields.append("level = %s")
            values.append(level)
        
        if not update_fields:
            return False
        
        # Always update updated_at and last_date
        update_fields.append("updated_at = NOW()")
        update_fields.append("last_date = %s")
        values.append(date.today())
        
        # Add telegram_id for WHERE clause
        values.append(telegram_id)
        
        query = f"""
            UPDATE api_telegramuser 
            SET {', '.join(update_fields)}
            WHERE telegram_id = %s
        """
        
        cursor.execute(query, values)
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Progress sync error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_all_telegram_users():
    """
    Django admin'dagi barcha Telegram userlarni olish
    """
    if not USE_POSTGRES or not DATABASE_URL:
        return []
    
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=3)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT telegram_id, username, first_name, correct, total, 
                   streak, level, created_at, updated_at
            FROM api_telegramuser
            ORDER BY created_at DESC
        """)
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"❌ Get users error: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


async def async_sync_telegram_user(telegram_id: int, username: str = None, first_name: str = None):
    """Run blocking sync in thread to keep bot responses fast."""
    return await asyncio.to_thread(sync_telegram_user, telegram_id, username, first_name)


async def async_update_user_progress(
    telegram_id: int,
    correct: int = None,
    total: int = None,
    streak: int = None,
    level: str = None,
):
    """Run blocking sync in thread to keep handlers non-blocking."""
    return await asyncio.to_thread(
        update_user_progress,
        telegram_id,
        correct,
        total,
        streak,
        level,
    )
