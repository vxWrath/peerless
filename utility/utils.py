import asyncio
from typing import Awaitable, Optional, List, Tuple
from thefuzz.process import extract
from thefuzz.utils import full_process
from unicodedata import normalize as unicode_normalize

from .logger import get_logger

logger = get_logger()

def create_logged_task[T](coro: Awaitable[T], *, name: Optional[str] = None, suppress_cancelled: bool = False) -> asyncio.Task[T]:
    """Wraps an asyncio.task for logging exceptions"""

    name = name or getattr(coro, '__name__', repr(coro))

    async def wrapper():
        try:
            return await coro
        except asyncio.CancelledError as e:
            if not suppress_cancelled:
                logger.warning(f"Task '{name}' was cancelled.", exc_info=e)
            raise e
        except Exception as e:
            logger.error(f"Task '{name}' raised an exception", exc_info=e)
            raise e

    task = asyncio.create_task(wrapper(), name=name)
    return task

def get_matches(query: str, choices: List[str], *, limit: int=5) -> List[Tuple[str, int]]:
    """Get the best matches for a query from a list of choices. Returns a list of tuples (choice, match_score [0-100])."""

    query = full_process(query, force_ascii=True) if query else query
    
    if not query:
        return [(x, 0) for x in choices][:limit]
    return extract(query=query, choices=choices, limit=limit)

def normalize(text: Optional[str]) -> str:
    """Normalize a string to ASCII. This removes accents and special characters.
    
    :param text: Optional[str] The string to normalize
    :return: str The normalized string
    """
    if text is None:
        return ''
    
    try:
        return unicode_normalize("NFKD", str(text)).encode('ascii', 'ignore').decode('utf-8')
    except Exception as e:
        logger.error("Failed to normalize text", exc_info=e)
        return ''