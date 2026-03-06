import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from config import ADMIN_IDS
from services.db import get_admin_stats, get_all_user_ids, block_user, is_user_blocked

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ Sizda admin huquqi yo'q")
        return

    stats = get_admin_stats()
    await message.answer(
        "📊 <b>Bot statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"📈 Bugun qo'shilgan: <b>{stats['today_joined']}</b>\n"
        f"⚡ Aktiv foydalanuvchilar: <b>{stats['active_users']}</b>\n\n"
        "Buyruqlar:\n"
        "• <code>/broadcast matn</code>\n"
        "• <code>/block USER_ID</code>\n"
        "• <code>/stats</code>",
        parse_mode="HTML",
    )


@router.message(Command("stats"))
async def admin_stats(message: types.Message):
    if not _is_admin(message.from_user.id):
        return

    stats = get_admin_stats()
    await message.answer(
        "📊 <b>Bot statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"📈 Bugun qo'shilgan: <b>{stats['today_joined']}</b>\n"
        f"⚡ Aktiv foydalanuvchilar: <b>{stats['active_users']}</b>",
        parse_mode="HTML",
    )


@router.message(Command("block"))
async def admin_block(message: types.Message):
    if not _is_admin(message.from_user.id):
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: /block USER_ID")
        return

    target_id = int(parts[1])
    if is_user_blocked(target_id):
        await message.answer("Bu foydalanuvchi allaqachon bloklangan")
        return

    block_user(target_id)
    await message.answer(f"✅ Bloklandi: <code>{target_id}</code>", parse_mode="HTML")


@router.message(Command("broadcast"))
async def admin_broadcast(message: types.Message):
    if not _is_admin(message.from_user.id):
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Foydalanish: /broadcast Xabar matni")
        return

    text = parts[1].strip()
    user_ids = get_all_user_ids()

    if not user_ids:
        await message.answer("Hali foydalanuvchilar topilmadi")
        return

    ok = 0
    failed = 0
    await message.answer(f"📢 Jo'natish boshlandi: {len(user_ids)} ta foydalanuvchi")

    for user_id in user_ids:
        if is_user_blocked(user_id):
            continue

        try:
            await message.bot.send_message(user_id, f"📢 <b>Yangilik</b>\n\n{text}", parse_mode="HTML")
            ok += 1
        except Exception:
            failed += 1

        # Telegram flood limitni yumshatish
        await asyncio.sleep(0.03)

    await message.answer(
        "✅ Broadcast tugadi\n\n"
        f"Yuborildi: {ok}\n"
        f"Xato: {failed}"
    )


def register(dp):
    dp.include_router(router)
