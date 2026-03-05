#!/usr/bin/env python3
"""
Database to'liq ma'lumotlarini ko'rsatish
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "bot"))

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("📊 NEON DATABASE HOLATI\n")
print("=" * 60)

# 1. Barcha jadvallar
print("\n1️⃣ JADVALLAR (barcha schemalar):")
cursor.execute("""
    SELECT schemaname, tablename 
    FROM pg_tables 
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    ORDER BY schemaname, tablename
""")
tables = cursor.fetchall()
for schema, table in tables:
    print(f"   ✅ {schema}.{table}")

if not tables:
    print("   ℹ️  Jadvallar topilmadi")

# 2. progress jadvalidagi ma'lumotlar
print("\n2️⃣ PROGRESS JADVALI:")
try:
    cursor.execute("SELECT * FROM progress ORDER BY user_id LIMIT 10")
    rows = cursor.fetchall()
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'progress' 
        ORDER BY ordinal_position
    """)
    columns = [col[0] for col in cursor.fetchall()]
    
    print(f"   Ustunlar: {', '.join(columns)}")
    print(f"   Qatorlar soni: {len(rows)}")
    
    if rows:
        print("\n   Ma'lumotlar:")
        for row in rows:
            print(f"   {dict(zip(columns, row))}")
    else:
        print("   ℹ️  Ma'lumotlar yo'q (test user hali saqlanmagan)")
        
except Exception as e:
    print(f"   ❌ Xatolik: {e}")

# 3. daily_lessons jadvali
print("\n3️⃣ DAILY_LESSONS JADVALI:")
try:
    cursor.execute("SELECT COUNT(*) FROM daily_lessons")
    count = cursor.fetchone()[0]
    print(f"   Qatorlar soni: {count}")
except Exception as e:
    print(f"   ❌ Xatolik: {e}")

# 4. Database meta info
print("\n4️⃣ DATABASE INFO:")
cursor.execute("SELECT current_database(), current_user, version()")
db_name, user, version = cursor.fetchone()
print(f"   Database: {db_name}")
print(f"   User: {user}")
print(f"   PostgreSQL: {version.split(',')[0]}")

# 5. Connection info
print("\n5️⃣ CONNECTION:")
print(f"   Host: {DATABASE_URL.split('@')[1].split('/')[0]}")
print(f"   SSL: {'✅ Enabled' if 'sslmode=require' in DATABASE_URL else '❌ Disabled'}")

conn.close()
print("\n" + "=" * 60)
print("✨ Database tekshiruvi tugadi!")
