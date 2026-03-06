from time import time

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from services.db import is_user_blocked, upsert_user

_LAST_SEEN_SYNC: dict[int, float] = {}
_SYNC_INTERVAL_SEC = 60


class UserContextMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = None

        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if not user:
            return await handler(event, data)

        now = time()
        last_sync = _LAST_SEEN_SYNC.get(user.id, 0)
        if now - last_sync >= _SYNC_INTERVAL_SEC:
            upsert_user(user.id, user.username, user.first_name)
            _LAST_SEEN_SYNC[user.id] = now

        if is_user_blocked(user.id):
            if isinstance(event, Message):
                await event.answer("⚠️ Siz bloklangansiz. Admin bilan bog'laning.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⚠️ Siz bloklangansiz.", show_alert=True)
            return None

        return await handler(event, data)
