#!/usr/bin/env python3
"""
To'g'ridan-to'g'ri PostgreSQL'ga jadval yaratish va tekshirish
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("🔧 PostgreSQL'ga to'g'ridan-to'g'ri ulanish...\n")

# Connect
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = False  # Explicit transaction mode

try:
    cursor = conn.cursor()
    
    print("1️⃣ progress jadvali yaratish...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            user_id BIGINT PRIMARY KEY,
            correct INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            last_date TEXT,
            level TEXT DEFAULT 'beginner'
        )
    """)
    print("   ✅ CREATE TABLE executed")
    
    print("\n2️⃣ daily_lessons jadvali yaratish...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_lessons (
            user_id BIGINT PRIMARY KEY,
            learned_date TEXT
        )
    """)
    print("   ✅ CREATE TABLE executed")
    
    print("\n3️⃣ COMMIT...")
    conn.commit()
    print("   ✅ COMMITTED")
    
    print("\n4️⃣ Jadvallarni tekshirish...")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"   ✅ Topilgan jadvallar: {[t[0] for t in tables]}")
    else:
        print("   ⚠️  Jadvallar topilmadi information_schema'da")
        
        # Alternative check using pg_tables
        print("\n5️⃣ pg_tables orqali tekshirish...")
        cursor.execute("""
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        pg_tables = cursor.fetchall()
        if pg_tables:
            print(f"   ✅ pg_tables: {pg_tables}")
        else:
            print("   ❌ pg_tables ham bo'sh")
    
    print("\n6️⃣ Test ma'lumot qo'shish...")
    cursor.execute("""
        INSERT INTO progress (user_id, level) 
        VALUES (999, 'intermediate')
        ON CONFLICT (user_id) DO UPDATE SET level='intermediate'
    """)
    conn.commit()
    print("   ✅ INSERT done")
    
    cursor.execute("SELECT * FROM progress WHERE user_id=999")
    row = cursor.fetchone()
    print(f"   ✅ SELECT result: {row}")
    
    print("\n✨ Hammasi muvaffaqiyatli!")
    
except Exception as e:
    print(f"\n❌ XATOLIK: {e}")
    conn.rollback()
    import traceback
    traceback.print_exc()
finally:
    conn.close()
