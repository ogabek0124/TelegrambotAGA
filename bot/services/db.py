import os
from datetime import date, timedelta
from pathlib import Path
from time import time

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
CACHE_TTL_SECONDS = int(os.getenv("BOT_CACHE_TTL", "20"))

_CACHE = {}


def _cache_get(key):
    item = _CACHE.get(key)
    if not item:
        return None
    expires_at, value = item
    if time() > expires_at:
        _CACHE.pop(key, None)
        return None
    return value


def _cache_set(key, value, ttl=CACHE_TTL_SECONDS):
    _CACHE[key] = (time() + ttl, value)


def _invalidate_cache(prefixes):
    keys = list(_CACHE.keys())
    for key in keys:
        if any(str(key).startswith(prefix) for prefix in prefixes):
            _CACHE.pop(key, None)


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

        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            referred_by BIGINT,
            referral_count INTEGER DEFAULT 0,
            bonus INTEGER DEFAULT 0,
            created_at TEXT,
            last_active TEXT
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS blocked_users (
            user_id BIGINT PRIMARY KEY,
            blocked_at TEXT
        )
        """)
        
        # Try to add level column if it doesn't exist (for old DBs)
        try:
            c.execute("ALTER TABLE progress ADD COLUMN level TEXT DEFAULT 'beginner'")
        except:
            pass
        
        conn.commit()
        _CACHE.clear()
        print("✅ Database tables created successfully")
    except Exception as e:
        conn.rollback()
        print(f"❌ Database init error: {e}")
        raise
    finally:
        conn.close()


def get_progress(user_id: int):
    """Get user progress stats"""
    cache_key = f"progress:{user_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"""
        SELECT correct, total, streak, last_date
        FROM progress WHERE user_id={placeholder}
        """, (user_id,))
        row = c.fetchone()
        result = row if row else (0, 0, 0, None)
        _cache_set(cache_key, result)
        return result


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
    _invalidate_cache((f"progress:{user_id}", f"streak:{user_id}", "leaderboard:"))


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
    _invalidate_cache((f"progress:{user_id}", f"streak:{user_id}", "leaderboard:"))


def get_streak(user_id: int):
    """Get user's current streak"""
    cache_key = f"streak:{user_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT streak FROM progress WHERE user_id={placeholder}", (user_id,))
        row = c.fetchone()
        result = row[0] if row else 0
        _cache_set(cache_key, result)
        return result


def get_leaderboard(limit: int = 10):
    """Get top users by streak and total score"""
    cache_key = f"leaderboard:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"""
        SELECT user_id, streak, total
        FROM progress
        ORDER BY streak DESC, total DESC
        LIMIT {placeholder}
        """, (limit,))
        result = c.fetchall()
        _cache_set(cache_key, result)
        return result


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
    _invalidate_cache((f"user_level:{user_id}",))


def get_user_level(user_id: int):
    """Get user's current learning level"""
    cache_key = f"user_level:{user_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT level FROM progress WHERE user_id={placeholder}", (user_id,))
        row = c.fetchone()
        result = row[0] if row and row[0] else None
        _cache_set(cache_key, result)
        return result


def upsert_user(user_id: int, username: str = None, first_name: str = None):
    """Store user profile for analytics/admin features."""
    placeholder = "%s" if USE_POSTGRES else "?"
    today = get_today()
    with get_connection() as conn:
        c = conn.cursor()
        if USE_POSTGRES:
            c.execute(f"""
            INSERT INTO users (user_id, username, first_name, created_at, last_active)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ON CONFLICT(user_id) DO UPDATE SET
                username=EXCLUDED.username,
                first_name=EXCLUDED.first_name,
                last_active=EXCLUDED.last_active
            """, (user_id, username, first_name, today, today))
        else:
            c.execute("""
            INSERT INTO users (user_id, username, first_name, created_at, last_active)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_active=excluded.last_active
            """, (user_id, username, first_name, today, today))
        conn.commit()
    _invalidate_cache(("admin_stats", "users:"))


def register_referral(user_id: int, referrer_id: int) -> bool:
    """Attach referrer to user once and increase referrer bonus counter."""
    if not referrer_id or user_id == referrer_id:
        return False

    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()

        # Ensure both users exist in the same transaction.
        if USE_POSTGRES:
            c.execute(
                f"INSERT INTO users (user_id, created_at, last_active) VALUES ({placeholder}, {placeholder}, {placeholder}) ON CONFLICT(user_id) DO NOTHING",
                (user_id, get_today(), get_today()),
            )
            c.execute(
                f"INSERT INTO users (user_id, created_at, last_active) VALUES ({placeholder}, {placeholder}, {placeholder}) ON CONFLICT(user_id) DO NOTHING",
                (referrer_id, get_today(), get_today()),
            )
        else:
            c.execute(
                "INSERT INTO users (user_id, created_at, last_active) VALUES (?, ?, ?) ON CONFLICT(user_id) DO NOTHING",
                (user_id, get_today(), get_today()),
            )
            c.execute(
                "INSERT INTO users (user_id, created_at, last_active) VALUES (?, ?, ?) ON CONFLICT(user_id) DO NOTHING",
                (referrer_id, get_today(), get_today()),
            )

        c.execute(f"SELECT referred_by FROM users WHERE user_id={placeholder}", (user_id,))
        row = c.fetchone()
        if row and row[0]:
            return False

        c.execute(
            f"UPDATE users SET referred_by={placeholder} WHERE user_id={placeholder} AND referred_by IS NULL",
            (referrer_id, user_id),
        )

        if c.rowcount <= 0:
            return False

        c.execute(
            f"UPDATE users SET referral_count=referral_count+1, bonus=bonus+1 WHERE user_id={placeholder}",
            (referrer_id,),
        )
        conn.commit()

    _invalidate_cache(("admin_stats", "users:"))
    return True


def is_user_blocked(user_id: int) -> bool:
    cache_key = f"blocked:{user_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT 1 FROM blocked_users WHERE user_id={placeholder}", (user_id,))
        result = c.fetchone() is not None
        _cache_set(cache_key, result, ttl=30)
        return result


def block_user(user_id: int):
    placeholder = "%s" if USE_POSTGRES else "?"
    with get_connection() as conn:
        c = conn.cursor()
        if USE_POSTGRES:
            c.execute(
                f"INSERT INTO blocked_users (user_id, blocked_at) VALUES ({placeholder}, {placeholder}) ON CONFLICT(user_id) DO NOTHING",
                (user_id, get_today()),
            )
        else:
            c.execute(
                "INSERT INTO blocked_users (user_id, blocked_at) VALUES (?, ?) ON CONFLICT(user_id) DO NOTHING",
                (user_id, get_today()),
            )
        conn.commit()
    _invalidate_cache((f"blocked:{user_id}",))


def get_all_user_ids():
    """All known user ids for broadcast."""
    cached = _cache_get("users:all_ids")
    if cached is not None:
        return cached

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        rows = c.fetchall()
        result = [row[0] for row in rows]
        _cache_set("users:all_ids", result, ttl=30)
        return result


def get_admin_stats():
    """Admin statistics: total/today/active users."""
    cached = _cache_get("admin_stats")
    if cached is not None:
        return cached

    with get_connection() as conn:
        c = conn.cursor()
        if USE_POSTGRES:
            c.execute("SELECT COUNT(*) FROM users")
            total = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE")
            today = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM users WHERE DATE(last_active) = CURRENT_DATE")
            active = c.fetchone()[0]
        else:
            today_str = get_today()
            c.execute("SELECT COUNT(*) FROM users")
            total = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?", (today_str,))
            today = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM users WHERE DATE(last_active) = ?", (today_str,))
            active = c.fetchone()[0]

        result = {
            "total_users": total,
            "today_joined": today,
            "active_users": active,
        }
        _cache_set("admin_stats", result, ttl=20)
        return result
