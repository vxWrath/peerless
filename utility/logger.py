import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import colorlog
import pytz
from discord.utils import setup_logging

if TYPE_CHECKING:
    from .bot import Bot

__all__ = (
    "get_logger",
    "setup_discord_logger",
)

class Formatter(colorlog.ColoredFormatter):
    def converter(self, timestamp):
        return datetime.fromtimestamp(timestamp=timestamp, tz=pytz.timezone('US/Central')).timetuple()

class DiscordHandler(colorlog.StreamHandler):
    def __init__(self, bot: 'Bot'):
        super().__init__()
        
        self.bot = bot
        
    def handle(self, record) -> bool:
        #if record.exc_info:
        #    self.bot.dispatch("error", "LOGGER", *record.exc_info)
        #    return True
        #else:
            return super().handle(record)
    
def _get_default_formatter(name: str) -> Formatter:
    """Return a default colorized formatter."""
    return Formatter(
        fmt=f"%(log_color)s[{name}][%(asctime)s][%(levelname)s] %(message)s",
        datefmt='%m/%d/%Y %I:%M:%S %p',
        log_colors={
            "DEBUG": "white",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

def get_logger(name: str = "peerless", level: int = logging.INFO, handler: Optional[logging.StreamHandler] = None) -> logging.Logger:
    """Create and return a colorized logger instance."""

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger # Prevent duplicate handlers

    logger.setLevel(level)

    if handler is None:
        handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = _get_default_formatter(name)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def setup_discord_logger(bot: 'Bot') ->  None:
    """Setup a logger that sends errors to the Discord bot."""

    setup_logging(
        handler=DiscordHandler(bot),
        formatter=_get_default_formatter("discord"),
        level=logging.INFO,
        root=False,
    )