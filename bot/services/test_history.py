"""
Test turlari va natijalar tarixi - database jadval
"""
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# Database connection
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
        import sqlite3
        return sqlite3.connect("data/progress.db")


def init_test_history():
    """Test natijalar tarixi jadvalini yaratish"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if USE_POSTGRES:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_history (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                test_type VARCHAR(50) NOT NULL,
                difficulty VARCHAR(20),
                correct INTEGER NOT NULL,
                total INTEGER NOT NULL,
                time_spent INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_type TEXT NOT NULL,
                difficulty TEXT,
                correct INTEGER NOT NULL,
                total INTEGER NOT NULL,
                time_spent INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ test_history jadvali yaratildi")


def save_test_result(user_id: int, test_type: str, correct: int, total: int, 
                     difficulty: str = "medium", time_spent: int = None):
    """Test natijasini saqlash"""
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholder = "%s" if USE_POSTGRES else "?"
    
    query = f"""
        INSERT INTO test_history (user_id, test_type, difficulty, correct, total, time_spent)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """
    
    cursor.execute(query, (user_id, test_type, difficulty, correct, total, time_spent))
    conn.commit()
    cursor.close()
    conn.close()


def get_test_history(user_id: int, limit: int = 10):
    """Foydalanuvchi test tarixini olish"""
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholder = "%s" if USE_POSTGRES else "?"
    
    query = f"""
        SELECT test_type, difficulty, correct, total, time_spent, completed_at
        FROM test_history
        WHERE user_id = {placeholder}
        ORDER BY completed_at DESC
        LIMIT {placeholder}
    """
    
    cursor.execute(query, (user_id, limit))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results


def get_test_stats(user_id: int):
    """Test statistikasi"""
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholder = "%s" if USE_POSTGRES else "?"
    
    query = f"""
        SELECT 
            COUNT(*) as total_tests,
            SUM(correct) as total_correct,
            SUM(total) as total_questions,
            AVG(CAST(correct AS FLOAT) / CAST(total AS FLOAT) * 100) as avg_percentage
        FROM test_history
        WHERE user_id = {placeholder}
    """
    
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return result


if __name__ == "__main__":
    init_test_history()
