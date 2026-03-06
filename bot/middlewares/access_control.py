from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from services.db import is_user_blocked


class AccessControlMiddleware(BaseMiddleware):
    """Blocks actions from users marked as blocked in database."""

    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        if not is_user_blocked(user.id):
            return await handler(event, data)

        if isinstance(event, CallbackQuery):
            await event.answer("⚠️ Siz vaqtincha bloklangansiz.", show_alert=True)
            return None

        if isinstance(event, Message):
            await event.answer("⚠️ Siz vaqtincha bloklangansiz.")
            return None

        return None
