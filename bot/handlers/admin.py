import os
from typing import Dict

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.db import (
    get_admin_stats,
    get_all_active_user_ids,
    mark_user_inactive,
    set_user_blocked,
)

router = Router()

ADMIN_STATES: Dict[int, str] = {}


def _admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_IDS", "")
    values = {v.strip() for v in raw.split(",") if v.strip()}
    return {int(v) for v in values if v.isdigit()}


def _is_admin(user_id: int) -> bool:
    return user_id in _admin_ids()


def get_admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")],
            [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin:broadcast")],
            [InlineKeyboardButton(text="🚫 Foydalanuvchini bloklash", callback_data="admin:block")],
            [InlineKeyboardButton(text="⚡ Aktiv foydalanuvchilar", callback_data="admin:active")],
            [InlineKeyboardButton(text="🏠 Menu", callback_data="back:main")],
        ]
    )


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ Sizda admin ruxsat yo'q.")
        return

    await message.answer(
        "🛠 <b>Admin panel</b>\n\nKerakli bo'limni tanlang:",
        parse_mode="HTML",
        reply_markup=get_admin_menu(),
    )


@router.callback_query(F.data.startswith("admin:"))
async def admin_actions(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not _is_admin(user_id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return

    action = callback.data.split(":", 1)[1]

    if action == "stats":
        stats = get_admin_stats()
        await callback.message.edit_text(
            "📊 <b>Bot statistikasi</b>\n\n"
            f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
            f"📈 Bugun qo'shilgan: <b>{stats['today_joined']}</b>\n"
            f"🟢 Bugun kirganlar (seen): <b>{stats['seen_today']}</b>\n"
            f"⚡ Aktiv foydalanuvchilar: <b>{stats['active_users']}</b>\n"
            f"🔴 Inaktiv (chiqqan/xato): <b>{stats['inactive_users']}</b>\n"
            f"🚫 Bloklanganlar: <b>{stats['blocked_users']}</b>",
            parse_mode="HTML",
            reply_markup=get_admin_menu(),
        )
        return

    if action == "active":
        stats = get_admin_stats()
        await callback.message.edit_text(
            "⚡ <b>Aktiv foydalanuvchilar</b>\n\n"
            f"Bugungi kirganlar (seen): <b>{stats['seen_today']}</b>\n"
            f"Aktiv userlar: <b>{stats['active_users']}</b>\n"
            f"Inaktiv userlar: <b>{stats['inactive_users']}</b>",
            parse_mode="HTML",
            reply_markup=get_admin_menu(),
        )
        return

    if action == "broadcast":
        ADMIN_STATES[user_id] = "broadcast"
        await callback.message.answer(
            "📢 Yuboriladigan xabar matnini kiriting.\n\nBekor qilish: /admin"
        )
        return

    if action == "block":
        ADMIN_STATES[user_id] = "block"
        await callback.message.answer(
            "🚫 Bloklash uchun foydalanuvchi `user_id` ni yuboring.\n\nBekor qilish: /admin",
            parse_mode="Markdown",
        )
        return


@router.message(lambda m: m.from_user is not None and m.from_user.id in ADMIN_STATES)
async def admin_state_input(message: types.Message):
    user_id = message.from_user.id
    state = ADMIN_STATES.get(user_id)

    if not state or not _is_admin(user_id):
        return

    if state == "block":
        raw = (message.text or "").strip()
        if not raw.isdigit():
            await message.answer("❌ Noto'g'ri ID. Faqat raqam yuboring.")
            return

        target_user_id = int(raw)
        set_user_blocked(target_user_id, True)
        ADMIN_STATES.pop(user_id, None)
        await message.answer(
            f"✅ User bloklandi: <code>{target_user_id}</code>",
            parse_mode="HTML",
            reply_markup=get_admin_menu(),
        )
        return

    if state == "broadcast":
        text = (message.text or "").strip()
        if not text:
            await message.answer("❌ Bo'sh xabar yuborib bo'lmaydi.")
            return

        ADMIN_STATES.pop(user_id, None)
        users = get_all_active_user_ids()
        sent = 0
        failed = 0


        for uid in users:
            try:
                await message.bot.send_message(uid, f"📢 <b>Yangilik</b>\n\n{text}", parse_mode="HTML")
                sent += 1
            except Exception:
                failed += 1
                mark_user_inactive(uid)

        await message.answer(
            "✅ <b>Broadcast yakunlandi</b>\n\n"
            f"📨 Yuborildi: <b>{sent}</b>\n"
            f"❌ Xato: <b>{failed}</b>",
            parse_mode="HTML",
            reply_markup=get_admin_menu(),
        )


def register(dp):
    dp.include_router(router)
