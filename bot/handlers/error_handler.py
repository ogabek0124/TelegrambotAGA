from aiogram import Router
from aiogram.types import ErrorEvent

router = Router()


@router.error()
async def global_error_handler(event: ErrorEvent):
    update = event.update
    message = "⚠️ Xatolik yuz berdi.\nIltimos qayta urinib ko'ring."

    try:
        if getattr(update, "message", None):
            await update.message.answer(message)
        elif getattr(update, "callback_query", None):
            await update.callback_query.answer("⚠️ Xatolik yuz berdi.", show_alert=True)
            if update.callback_query.message:
                await update.callback_query.message.answer(message)
    except Exception:
        pass

    return True


def register(dp):
    dp.include_router(router)
