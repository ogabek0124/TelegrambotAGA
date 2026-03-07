import os
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from threading import Lock
from time import time
from typing import Optional

# Try PostgreSQL first, fallback to SQLite for local dev
try:
    import psycopg2

    USE_POSTGRES = bool(os.getenv("DATABASE_URL"))
except ImportError:
    USE_POSTGRES = False

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_NAME = str(DATA_DIR / "progress.db")
DATABASE_URL = os.getenv("DATABASE_URL")

# Small in-memory cache for hot reads.
_CACHE: dict[str, tuple[float, object]] = {}
_CACHE_LOCK = Lock()
CACHE_TTL_SEC = 30
_SCHEMA_READY = False
_SCHEMA_LOCK = Lock()


def _cache_get(key: str):
    with _CACHE_LOCK:
        item = _CACHE.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at < time():
            _CACHE.pop(key, None)
            return None
        return value


def _cache_set(key: str, value, ttl: int = CACHE_TTL_SEC):
    with _CACHE_LOCK:
        _CACHE[key] = (time() + ttl, value)


def _cache_invalidate(prefix: str):
    with _CACHE_LOCK:
        keys = [k for k in _CACHE.keys() if k.startswith(prefix)]
        for key in keys:
            _CACHE.pop(key, None)


def _open_connection():
    """Open a raw DB connection without running migrations/bootstrap."""
    if USE_POSTGRES and DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, connect_timeout=3)

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def _apply_schema(cursor):
    """Create required tables and perform additive migrations safely."""
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS progress (
        user_id BIGINT PRIMARY KEY,
        correct INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        last_date TEXT,
        level TEXT DEFAULT 'beginner'
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS daily_lessons (
        user_id BIGINT PRIMARY KEY,
        learned_date TEXT
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS bot_users (
        user_id BIGINT PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        blocked INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        referred_by BIGINT,
        referrals_count INTEGER DEFAULT 0,
        last_seen TEXT,
        created_at TEXT
    )
    """
    )

    migration_columns = [
        ("blocked", "INTEGER DEFAULT 0"),
        ("is_active", "INTEGER DEFAULT 1"),
        ("referred_by", "BIGINT"),
        ("referrals_count", "INTEGER DEFAULT 0"),
        ("last_seen", "TEXT"),
        ("created_at", "TEXT"),
        ("username", "TEXT"),
        ("first_name", "TEXT"),
    ]
    for col_name, col_type in migration_columns:
        try:
            cursor.execute(f"ALTER TABLE bot_users ADD COLUMN {col_name} {col_type}")
        except Exception:
            pass

    try:
        cursor.execute("ALTER TABLE progress ADD COLUMN level TEXT DEFAULT 'beginner'")
    except Exception:
        pass


def get_connection():
    """Get DB connection and lazily ensure schema exists (one-time per process)."""
    global _SCHEMA_READY

    conn = _open_connection()
    if _SCHEMA_READY:
        return conn

    with _SCHEMA_LOCK:
        if _SCHEMA_READY:
            return conn
        try:
            c = conn.cursor()
            _apply_schema(c)
            conn.commit()
            _SCHEMA_READY = True
        except Exception:
            conn.rollback()
            raise

    return conn


def _ph() -> str:
    return "%s" if USE_POSTGRES else "?"


def init_db():
    """Initialize database tables."""
    global _SCHEMA_READY

    conn = _open_connection()
    try:
        c = conn.cursor()
        _apply_schema(c)

        conn.commit()
        _SCHEMA_READY = True
        print("✅ Database tables created successfully")
    except Exception as e:
        conn.rollback()
        print(f"❌ Database init error: {e}")
        raise
    finally:
        conn.close()


def get_today():
    return date.today().isoformat()


def _today_dt_str() -> str:
    return date.today().isoformat()


def upsert_user(user_id: int, username: Optional[str] = None, first_name: Optional[str] = None):
    """Track user metadata for admin panel, broadcast and referral stats."""
    placeholder = _ph()
    today = _today_dt_str()

    with get_connection() as conn:
        c = conn.cursor()
        if USE_POSTGRES:
            c.execute(
                f"""
                INSERT INTO bot_users (user_id, username, first_name, last_seen, created_at)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                ON CONFLICT(user_id) DO UPDATE SET
                    username = COALESCE(EXCLUDED.username, bot_users.username),
                    first_name = COALESCE(EXCLUDED.first_name, bot_users.first_name),
                    last_seen = EXCLUDED.last_seen,
                    is_active = 1
                """,
                (user_id, username, first_name, today, today),
            )
        else:
            c.execute(
                """
                INSERT INTO bot_users (user_id, username, first_name, last_seen, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = COALESCE(excluded.username, bot_users.username),
                    first_name = COALESCE(excluded.first_name, bot_users.first_name),
                    last_seen = excluded.last_seen,
                    is_active = 1
                """,
                (user_id, username, first_name, today, today),
            )
        conn.commit()

    _cache_invalidate("stats:")


def is_user_blocked(user_id: int) -> bool:
    cache_key = f"user_blocked:{user_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return bool(cached)

    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT blocked FROM bot_users WHERE user_id={placeholder}", (user_id,))
        row = c.fetchone()
        blocked = bool(row[0]) if row else False

    _cache_set(cache_key, blocked, ttl=20)
    return blocked


def set_user_blocked(user_id: int, blocked: bool) -> bool:
    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()
        if USE_POSTGRES:
            c.execute(
                f"""
                INSERT INTO bot_users (user_id, blocked, last_seen, created_at)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                ON CONFLICT(user_id) DO UPDATE SET blocked = EXCLUDED.blocked
                """,
                (user_id, 1 if blocked else 0, _today_dt_str(), _today_dt_str()),
            )
        else:
            c.execute(
                """
                INSERT INTO bot_users (user_id, blocked, last_seen, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET blocked = excluded.blocked
                """,
                (user_id, 1 if blocked else 0, _today_dt_str(), _today_dt_str()),
            )
        conn.commit()

    _cache_set(f"user_blocked:{user_id}", blocked, ttl=60)
    _cache_invalidate("stats:")
    return True


def add_referral(new_user_id: int, referrer_id: int) -> bool:
    """Attach referral once for a user and increment referrer counter."""
    if not referrer_id or referrer_id == new_user_id:
        return False

    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT referred_by FROM bot_users WHERE user_id={placeholder}", (new_user_id,))
        row = c.fetchone()

        if row and row[0]:
            return False

        if USE_POSTGRES:
            c.execute(
                f"""
                INSERT INTO bot_users (user_id, referred_by, last_seen, created_at)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                ON CONFLICT(user_id) DO UPDATE SET referred_by = EXCLUDED.referred_by
                """,
                (new_user_id, referrer_id, _today_dt_str(), _today_dt_str()),
            )
            c.execute(
                f"""
                INSERT INTO bot_users (user_id, referrals_count, last_seen, created_at)
                VALUES ({placeholder}, 1, {placeholder}, {placeholder})
                ON CONFLICT(user_id) DO UPDATE SET referrals_count = bot_users.referrals_count + 1
                """,
                (referrer_id, _today_dt_str(), _today_dt_str()),
            )
        else:
            c.execute(
                """
                INSERT INTO bot_users (user_id, referred_by, last_seen, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET referred_by = excluded.referred_by
                """,
                (new_user_id, referrer_id, _today_dt_str(), _today_dt_str()),
            )
            c.execute(
                """
                INSERT INTO bot_users (user_id, referrals_count, last_seen, created_at)
                VALUES (?, 1, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET referrals_count = bot_users.referrals_count + 1
                """,
                (referrer_id, _today_dt_str(), _today_dt_str()),
            )

        conn.commit()

    _cache_invalidate("stats:")
    return True


def get_referrals_count(user_id: int) -> int:
    placeholder = _ph()
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute(f"SELECT referrals_count FROM bot_users WHERE user_id={placeholder}", (user_id,))
            row = c.fetchone()
            return int(row[0]) if row and row[0] else 0
    except Exception as exc:
        # In case schema bootstrap was skipped on a stale connection, initialize and retry once.
        if "bot_users" in str(exc) and "does not exist" in str(exc):
            init_db()
            with get_connection() as conn:
                c = conn.cursor()
                c.execute(f"SELECT referrals_count FROM bot_users WHERE user_id={placeholder}", (user_id,))
                row = c.fetchone()
                return int(row[0]) if row and row[0] else 0
        raise


def get_progress(user_id: int):
    """Get user progress stats."""
    cache_key = f"progress:{user_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"""
        SELECT correct, total, streak, last_date
        FROM progress WHERE user_id={placeholder}
        """,
            (user_id,),
        )
        row = c.fetchone()
        value = row if row else (0, 0, 0, None)

    _cache_set(cache_key, value)
    return value


def update_streak(user_id: int):
    """Update user's daily streak."""
    correct, total, streak, last_date = get_progress(user_id)
    today = date.today()

    if last_date:
        last = date.fromisoformat(last_date)
        if today == last:
            return
        if today == last + timedelta(days=1):
            streak += 1
        else:
            streak = 1
    else:
        streak = 1

    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()

        if USE_POSTGRES:
            c.execute(
                f"""
                INSERT INTO progress (user_id, streak, last_date)
                VALUES ({placeholder}, {placeholder}, {placeholder})
                ON CONFLICT(user_id) DO UPDATE SET
                    streak=EXCLUDED.streak,
                    last_date=EXCLUDED.last_date
                """,
                (user_id, streak, get_today()),
            )
        else:
            c.execute(
                """
                INSERT INTO progress (user_id, streak, last_date)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    streak=excluded.streak,
                    last_date=excluded.last_date
                """,
                (user_id, streak, get_today()),
            )

        conn.commit()

    _cache_set(f"progress:{user_id}", (correct, total, streak, get_today()))
    _cache_invalidate("stats:")


def save_progress(user_id: int, is_correct: bool):
    """Save user's test/quiz progress using one read and one write."""
    correct, total, streak, last_date = get_progress(user_id)

    total += 1
    if is_correct:
        correct += 1

    today = date.today()
    new_streak = streak
    if last_date:
        last = date.fromisoformat(last_date)
        if today == last:
            new_streak = streak
        elif today == last + timedelta(days=1):
            new_streak = streak + 1
        else:
            new_streak = 1
    else:
        new_streak = 1

    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()

        if USE_POSTGRES:
            c.execute(
                f"""
                INSERT INTO progress (user_id, correct, total, streak, last_date)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                ON CONFLICT(user_id) DO UPDATE SET
                    correct=EXCLUDED.correct,
                    total=EXCLUDED.total,
                    streak=EXCLUDED.streak,
                    last_date=EXCLUDED.last_date
                """,
                (user_id, correct, total, new_streak, get_today()),
            )
        else:
            c.execute(
                """
                INSERT INTO progress (user_id, correct, total, streak, last_date)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    correct=excluded.correct,
                    total=excluded.total,
                    streak=excluded.streak,
                    last_date=excluded.last_date
                """,
                (user_id, correct, total, new_streak, get_today()),
            )

        conn.commit()

    _cache_set(f"progress:{user_id}", (correct, total, new_streak, get_today()))
    _cache_invalidate("stats:")


def get_streak(user_id: int):
    """Get user's current streak."""
    progress = get_progress(user_id)
    return int(progress[2]) if progress else 0


def get_leaderboard(limit: int = 10):
    """Get top users by streak and total score."""
    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            f"""
        SELECT user_id, streak, total
        FROM progress
        ORDER BY streak DESC, total DESC
        LIMIT {placeholder}
        """,
            (limit,),
        )
        return c.fetchall()


def set_user_level(user_id: int, level: str):
    """Set user's learning level."""
    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()

        if USE_POSTGRES:
            c.execute(
                f"""
                INSERT INTO progress (user_id)
                VALUES ({placeholder})
                ON CONFLICT(user_id) DO NOTHING
                """,
                (user_id,),
            )
            c.execute(
                f"""
                UPDATE progress SET level={placeholder}
                WHERE user_id={placeholder}
                """,
                (level, user_id),
            )
        else:
            c.execute(
                """
                INSERT INTO progress (user_id)
                VALUES (?)
                ON CONFLICT(user_id) DO NOTHING
                """,
                (user_id,),
            )
            c.execute(
                """
                UPDATE progress SET level=?
                WHERE user_id=?
                """,
                (level, user_id),
            )

        conn.commit()

    _cache_set(f"level:{user_id}", level)
    _cache_invalidate("stats:")


def get_user_level(user_id: int):
    """Get user's current learning level."""
    cache_key = f"level:{user_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT level FROM progress WHERE user_id={placeholder}", (user_id,))
        row = c.fetchone()
        level = row[0] if row and row[0] else None

    _cache_set(cache_key, level)
    return level


def get_all_active_user_ids() -> list[int]:
    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT user_id FROM bot_users WHERE blocked={placeholder}", (0,))
        rows = c.fetchall() or []
    return [int(r[0]) for r in rows]


def mark_user_inactive(user_id: int):
    placeholder = _ph()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"UPDATE bot_users SET is_active=0 WHERE user_id={placeholder}", (user_id,))
        conn.commit()
    _cache_invalidate("stats:")


def get_admin_stats() -> dict:
    cache_key = "stats:admin"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    today = _today_dt_str()
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM bot_users")
        total_users = int(c.fetchone()[0] or 0)

        placeholder = _ph()
        c.execute(f"SELECT COUNT(*) FROM bot_users WHERE created_at={placeholder}", (today,))
        today_joined = int(c.fetchone()[0] or 0)

        c.execute(f"SELECT COUNT(*) FROM bot_users WHERE is_active={placeholder} AND blocked={placeholder}", (1, 0))
        active_users = int(c.fetchone()[0] or 0)

    payload = {
        "total_users": total_users,
        "today_joined": today_joined,
        "active_users": active_users,
    }
    _cache_set(cache_key, payload, ttl=15)
    return payload
