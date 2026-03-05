#!/usr/bin/env python3
"""
Qaysi database ishlatilayotganini aniqlash
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "bot"))

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 DATABASE KONFIGURATSIYASI:\n")
print("=" * 60)

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"📝 DATABASE_URL: {DATABASE_URL[:50]}...")

# Check services/db module
from services import db

print(f"\n✅ USE_POSTGRES = {db.USE_POSTGRES}")
print(f"✅ DATABASE_URL (from db.py) = {db.DATABASE_URL[:50] if db.DATABASE_URL else 'None'}...")
print(f"✅ DB_NAME (SQLite path) = {db.DB_NAME}")

if db.USE_POSTGRES:
    print("\n🐘 PostgreSQL rejimi active")
    print(f"   Psycopg2 imported: {'✅ Yes' if 'psycopg2' in sys.modules else '❌ No'}")
else:
    print("\n🗄️  SQLite rejimi active (PostgreSQL o'rniga)")
    print(f"   SQLite3 imported: {'✅ Yes' if 'sqlite3' in sys.modules else '❌ No'}")

# Test connection
print("\n🔌 CONNECTION TEST:")
try:
    conn = db.get_connection()
    print(f"   Type: {type(conn)}")
    print(f"   ✅ Connection successful!")
    
    if db.USE_POSTGRES:
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"   PostgreSQL: {version.split(',')[0]}")
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        print(f"   SQLite: {version}")
    
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
