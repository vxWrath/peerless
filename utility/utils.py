import asyncio
from typing import Any, Coroutine, Optional

from .logger import get_logger

logger = get_logger()

def create_logged_task[T](coro: Coroutine[Any, Any, T], *, name: Optional[str] = None, suppress_cancelled: bool = False) -> asyncio.Task[T]:
    """Wraps an asyncio.task for logging exceptions"""

    async def wrapper():
        try:
            return await coro
        except asyncio.CancelledError as e:
            if not suppress_cancelled:
                logger.warning(f"Task '{name or coro.__name__}' was cancelled.", exc_info=e)
            raise e
        except Exception as e:
            logger.error(f"Task '{name or coro.__name__}' raised an exception", exc_info=e)
            raise e

    task = asyncio.create_task(wrapper())
    return task