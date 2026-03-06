import logging
from aiogram import Router
from aiogram.types import ErrorEvent

router = Router()
logger = logging.getLogger(__name__)


@router.error()
async def global_error_handler(event: ErrorEvent):
    """Show user-friendly error instead of silent crash."""
    logger.exception("Unhandled bot error", exc_info=event.exception)

    update = event.update
    if update and update.callback_query:
        callback = update.callback_query
        try:
            await callback.answer("⚠️ Xatolik yuz berdi.\nIltimos qayta urinib ko'ring.", show_alert=True)
        except Exception:
            pass
        return True

    if update and update.message:
        try:
            await update.message.answer("⚠️ Xatolik yuz berdi.\nIltimos qayta urinib ko'ring.")
        except Exception:
            pass
        return True

    return True


def register(dp):
    dp.include_router(router)
