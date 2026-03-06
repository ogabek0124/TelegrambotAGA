import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from config import ADMIN_IDS
from services.db import (
    get_all_user_ids,
    block_user,
    unblock_user,
    is_user_blocked,
)
from services.logic import format_stats_message

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def _parse_target_user_id(text: str) -> int | None:
    parts = (text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        return None
    return int(parts[1])


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ Sizda admin huquqi yo'q")
        return

    await message.answer(
        format_stats_message() + "\n\n"
        "Buyruqlar:\n"
        "• <code>/broadcast matn</code>\n"
        "• <code>/block USER_ID</code>\n"
        "• <code>/unblock USER_ID</code>\n"
        "• <code>/stats</code>",
        parse_mode="HTML",
    )


@router.message(Command("stats"))
async def admin_stats(message: types.Message):
    if not _is_admin(message.from_user.id):
        return

    await message.answer(format_stats_message(), parse_mode="HTML")


@router.message(Command("block"))
async def admin_block(message: types.Message):
    if not _is_admin(message.from_user.id):
        return

    target_id = _parse_target_user_id(message.text or "")
    if target_id is None:
        await message.answer("Foydalanish: /block USER_ID")
        return

    if is_user_blocked(target_id):
        await message.answer("Bu foydalanuvchi allaqachon bloklangan")
        return

    block_user(target_id)
    await message.answer(f"✅ Bloklandi: <code>{target_id}</code>", parse_mode="HTML")


@router.message(Command("unblock"))
async def admin_unblock(message: types.Message):
    if not _is_admin(message.from_user.id):
        return

    target_id = _parse_target_user_id(message.text or "")
    if target_id is None:
        await message.answer("Foydalanish: /unblock USER_ID")
        return

    if not is_user_blocked(target_id):
        await message.answer("Bu foydalanuvchi bloklanmagan")
        return

    unblock_user(target_id)
    await message.answer(f"✅ Blockdan chiqarildi: <code>{target_id}</code>", parse_mode="HTML")


async def _send_with_retry(bot, user_id: int, text: str, retries: int = 2) -> bool:
    for attempt in range(retries + 1):
        try:
            await bot.send_message(user_id, text, parse_mode="HTML")
            return True
        except Exception:
            if attempt >= retries:
                return False
            await asyncio.sleep(0.2 * (attempt + 1))
    return False


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
    skipped = 0
    batch_size = 25

    progress_message = await message.answer(f"🔍 Foydalanuvchilar tayyorlandi.\n📢 Jo'natish boshlandi: {len(user_ids)} ta foydalanuvchi")

    payload = f"📢 <b>Yangilik</b>\n\n{text}"

    for start in range(0, len(user_ids), batch_size):
        batch = user_ids[start:start + batch_size]
        tasks = []

        for user_id in batch:
            if is_user_blocked(user_id):
                skipped += 1
                continue
            tasks.append(_send_with_retry(message.bot, user_id, payload))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=False)
            ok += sum(1 for item in results if item)
            failed += sum(1 for item in results if not item)

        try:
            await progress_message.edit_text(
                "📡 Broadcast davom etmoqda...\n\n"
                f"Jo'natildi: {ok}\n"
                f"Xato: {failed}\n"
                f"Skip (blocked): {skipped}\n"
                f"Progress: {min(start + batch_size, len(user_ids))}/{len(user_ids)}"
            )
        except Exception:
            pass

        # Flood ehtimolini kamaytirish uchun batchlar orasida kichik pauza.
        await asyncio.sleep(0.25)

    await message.answer(
        "✅ Broadcast tugadi\n\n"
        f"Yuborildi: {ok}\n"
        f"Xato: {failed}\n"
        f"Skip (blocked): {skipped}"
    )


def register(dp):
    dp.include_router(router)
