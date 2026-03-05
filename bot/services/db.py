import sqlite3
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_NAME = str(DATA_DIR / "progress.db")


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER PRIMARY KEY,
            correct INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            last_date TEXT,
            level TEXT DEFAULT 'beginner'
        )
        """)
        
        # Daily lessons table
        c.execute("""
        CREATE TABLE IF NOT EXISTS daily_lessons (
            user_id INTEGER PRIMARY KEY,
            learned_date TEXT
        )
        """)
        
        # Level column qo'shish (agar bo'lmasa)
        try:
            c.execute("ALTER TABLE progress ADD COLUMN level TEXT DEFAULT 'beginner'")
        except:
            pass
        
        conn.commit()


def get_progress(user_id: int):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        SELECT correct, total, streak, last_date
        FROM progress WHERE user_id=?
        """, (user_id,))
        row = c.fetchone()
        return row if row else (0, 0, 0, None)


def get_today():
    return date.today().isoformat()


def update_streak(user_id: int):
    correct, total, streak, last_date = get_progress(user_id)
    today = date.today()

    if last_date:
        last = date.fromisoformat(last_date)
        if today == last:
            return
        elif today == last + timedelta(days=1):
            streak += 1
        else:
            streak = 1
    else:
        streak = 1

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO progress (user_id, streak, last_date)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            streak=?,
            last_date=?
        """, (user_id, streak, get_today(), streak, get_today()))
        conn.commit()


def save_progress(user_id: int, is_correct: bool):
    correct, total, _, _ = get_progress(user_id)

    total += 1
    if is_correct:
        correct += 1

    update_streak(user_id)
    streak = get_streak(user_id)

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO progress (user_id, correct, total, streak, last_date)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            correct=?,
            total=?,
            streak=?,
            last_date=?
        """, (
            user_id, correct, total, streak, get_today(),
            correct, total, streak, get_today()
        ))
        conn.commit()


def get_streak(user_id: int):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT streak FROM progress WHERE user_id=?", (user_id,))
        row = c.fetchone()
        return row[0] if row else 0


def get_leaderboard(limit: int = 10):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        SELECT user_id, streak, total
        FROM progress
        ORDER BY streak DESC, total DESC
        LIMIT ?
        """, (limit,))
        return c.fetchall()
def set_user_level(user_id: int, level: str):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO progress (user_id)
        VALUES (?)
        ON CONFLICT(user_id) DO NOTHING
        """, (user_id,))
        c.execute("""
        UPDATE progress SET level=?
        WHERE user_id=?
        """, (level, user_id))
        conn.commit()


def get_user_level(user_id: int):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT level FROM progress WHERE user_id=?", (user_id,))
        row = c.fetchone()
        return row[0] if row and row[0] else None
