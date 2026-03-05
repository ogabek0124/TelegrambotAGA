#!/usr/bin/env python3
"""
Neon PostgreSQL connection testi
"""
import os
import sys
from pathlib import Path

# Bot modulini import qilish uchun
sys.path.insert(0, str(Path(__file__).parent / "bot"))

from dotenv import load_dotenv
load_dotenv()

def test_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL topilmadi!")
        print("📝 .env faylida DATABASE_URL ni to'ldiring")
        return False
    
    # PostgreSQL connection string tekshirish
    if not DATABASE_URL.startswith("postgresql://"):
        print("⚠️  DATABASE_URL SQLite formatida (PostgreSQL emas)")
        print(f"   Hozirgi: {DATABASE_URL}")
        return False
    
    print(f"✅ DATABASE_URL topildi")
    print(f"   Host: {DATABASE_URL.split('@')[1].split('/')[0]}")
    
    # Connection test
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Version check
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL connection muvaffaqiyatli!")
        print(f"   Version: {version.split(',')[0]}")
        
        # Tables check
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Mavjud jadvallar: {[t[0] for t in tables]}")
        else:
            print("ℹ️  Jadvallar hali yaratilmagan (bot ishga tushganda yaratiladi)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection xatosi: {e}")
        print("\n📋 Tekshirish kerak:")
        print("   1. Neon console'dan to'g'ri connection string ko'chirilganmi?")
        print("   2. IP address whitelist qo'shilganmi? (0.0.0.0/0 barcha IP uchun)")
        print("   3. Database 'production' branchda active holatdami?")
        return False

if __name__ == "__main__":
    print("🔍 Neon PostgreSQL connection testi...\n")
    success = test_connection()
    
    if success:
        print("\n✨ Database tayyor! Bot ishga tushishi mumkin.")
    else:
        print("\n❌ Database sozlash kerak.")
    
    sys.exit(0 if success else 1)
