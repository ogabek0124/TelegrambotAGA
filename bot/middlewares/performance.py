import logging
import time
from aiogram import BaseMiddleware

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseMiddleware):
    """Logs handlers slower than threshold for easier performance tuning."""

    def __init__(self, slow_threshold: float = 1.0):
        self.slow_threshold = slow_threshold

    async def __call__(self, handler, event, data):
        start = time.perf_counter()
        result = await handler(event, data)
        elapsed = time.perf_counter() - start

        if elapsed >= self.slow_threshold:
            user_id = getattr(getattr(event, "from_user", None), "id", "unknown")
            logger.warning("Slow handler: %.3fs | user_id=%s | event=%s", elapsed, user_id, event.__class__.__name__)

        return result
