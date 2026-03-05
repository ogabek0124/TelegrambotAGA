#!/usr/bin/env python3
"""
Database jadvallarini yaratish va tekshirish
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "bot"))

from services.db import init_db, set_user_level, get_user_level
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import psycopg2
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    print("🔧 Database jadvallarini yaratish...")
    init_db()
    print("✅ init_db() muvaffaqiyatli bajarildi!\n")
    
    # Jadvallarni tekshirish
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    if tables:
        print("📊 Yaratilgan jadvallar:")
        for table in tables:
            print(f"   ✅ {table[0]}")
            
            # Har bir jadvaldagi ustunlarni ko'rsatish
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table[0]}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            for col in columns:
                print(f"      - {col[0]} ({col[1]})")
            print()
    else:
        print("❌ Jadvallar yaratilmadi!")
    
    # Test user qo'shish
    print("🧪 Test: Foydalanuvchi qo'shish...")
    test_user_id = 123456789
    set_user_level(test_user_id, 'beginner')
    level = get_user_level(test_user_id)
    
    if level == 'beginner':
        print(f"✅ Test muvaffaqiyatli! User {test_user_id} darajasi: {level}")
    else:
        print(f"❌ Test xato! Kutilgan: beginner, Olindi: {level}")
    
    conn.close()
    print("\n✨ Database to'liq tayyor!")
    
except Exception as e:
    print(f"❌ Xatolik: {e}")
    import traceback
    traceback.print_exc()
