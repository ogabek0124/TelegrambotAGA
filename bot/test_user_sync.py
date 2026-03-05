"""
User sync funksiyalarini test qilish
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.user_sync import sync_telegram_user, update_user_progress, get_all_telegram_users

print("🧪 User Sync Test\n")

# Test 1: Yangi user sync qilish
print("1️⃣ Yangi user yaratish...")
result = sync_telegram_user(
    telegram_id=123456789,
    username="test_user",
    first_name="Test Foydalanuvchi"
)
print(f"   Sync result: {result}")

# Test 2: User progressini yangilash
print("\n2️⃣ User progressini yangilash...")
result = update_user_progress(
    telegram_id=123456789,
    correct=15,
    total=20,
    streak=3,
    level="intermediate"
)
print(f"   Update result: {result}")

# Test 3: Ikkinchi marta sync (update bo'lishi kerak)
print("\n3️⃣ Mavjud userni update qilish...")
result = sync_telegram_user(
    telegram_id=123456789,
    username="test_user_updated",
    first_name="Test User Updated"
)
print(f"   Sync result: {result}")

# Test 4: Barcha userlarni olish
print("\n4️⃣ Barcha userlar ro'yxati:")
users = get_all_telegram_users()
if users:
    for user in users:
        print(f"   👤 {user.get('first_name')} (@{user.get('username')}) - {user.get('level')} - {user.get('correct')}/{user.get('total')}")
else:
    print("   Userlar yo'q yoki xatolik yuz berdi")

print("\n✅ Test tugadi!")
