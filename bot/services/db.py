import os
from datetime import date, timedelta
from pathlib import Path

# Try PostgreSQL first, fallback to SQLite for local dev
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_POSTGRES = bool(os.getenv("DATABASE_URL"))
except ImportError:
    USE_POSTGRES = False

if not USE_POSTGRES:
    import sqlite3

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_NAME = str(DATA_DIR / "progress.db")
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Get database connection - PostgreSQL in production, SQLite locally"""
    if USE_POSTGRES and DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        return sqlite3.connect(DB_NAME)


def init_db():
    """Initialize database tables"""
    conn = get_connection()
    try:
        c = conn.cursor()
        
        # Progress table - same structure for both databases
        c.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            user_id BIGINT PRIMARY KEY,
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
            user_id BIGINT PRIMARY KEY,
            learned_date TEXT
        )
        """)
        
        # Try to add level column if it doesn't exist (for old DBs)
        try:
            c.execute("ALTER TABLE progress ADD COLUMN level TEXT DEFAULT 'beginner'")
        except:
            pass
        
        conn.commit()
        print("✅ Database tables created successfully")
    except Exception as e:
        conn.rollback()
        print(f"❌ Database init error: {e}")
        raise
    finally:
        conn.close()


def get_progress(user_id: int):
    """Get user progress stats"""
    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"""
        SELECT correct, total, streak, last_date
        FROM progress WHERE user_id={placeholder}
        """, (user_id,))
        row = c.fetchone()
        return row if row else (0, 0, 0, None)


def get_today():
    return date.today().isoformat()


def update_streak(user_id: int):
    """Update user's daily streak"""
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

    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        
        if USE_POSTGRES:
            # PostgreSQL uses INSERT ... ON CONFLICT
            c.execute(f"""
            INSERT INTO progress (user_id, streak, last_date)
            VALUES ({placeholder}, {placeholder}, {placeholder})
            ON CONFLICT(user_id) DO UPDATE SET
                streak=EXCLUDED.streak,
                last_date=EXCLUDED.last_date
            """, (user_id, streak, get_today()))
        else:
            # SQLite uses INSERT ... ON CONFLICT
            c.execute("""
            INSERT INTO progress (user_id, streak, last_date)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                streak=?,
                last_date=?
            """, (user_id, streak, get_today(), streak, get_today()))
        
        conn.commit()


def save_progress(user_id: int, is_correct: bool):
    """Save user's test/quiz progress"""
    correct, total, _, _ = get_progress(user_id)

    total += 1
    if is_correct:
        correct += 1

    update_streak(user_id)
    streak = get_streak(user_id)

    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        
        if USE_POSTGRES:
            # PostgreSQL ON CONFLICT syntax
            c.execute(f"""
            INSERT INTO progress (user_id, correct, total, streak, last_date)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ON CONFLICT(user_id) DO UPDATE SET
                correct=EXCLUDED.correct,
                total=EXCLUDED.total,
                streak=EXCLUDED.streak,
                last_date=EXCLUDED.last_date
            """, (user_id, correct, total, streak, get_today()))
        else:
            # SQLite ON CONFLICT syntax
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
    """Get user's current streak"""
    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT streak FROM progress WHERE user_id={placeholder}", (user_id,))
        row = c.fetchone()
        return row[0] if row else 0


def get_leaderboard(limit: int = 10):
    """Get top users by streak and total score"""
    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"""
        SELECT user_id, streak, total
        FROM progress
        ORDER BY streak DESC, total DESC
        LIMIT {placeholder}
        """, (limit,))
        return c.fetchall()


def set_user_level(user_id: int, level: str):
    """Set user's learning level"""
    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        
        if USE_POSTGRES:
            c.execute(f"""
            INSERT INTO progress (user_id)
            VALUES ({placeholder})
            ON CONFLICT(user_id) DO NOTHING
            """, (user_id,))
            c.execute(f"""
            UPDATE progress SET level={placeholder}
            WHERE user_id={placeholder}
            """, (level, user_id))
        else:
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
    """Get user's current learning level"""
    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT level FROM progress WHERE user_id={placeholder}", (user_id,))
        row = c.fetchone()
        return row[0] if row and row[0] else None
