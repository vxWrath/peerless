import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import colorlog
import pytz

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

def get_logger(name: str = "peerless", level: int = logging.DEBUG, handler: Optional[logging.StreamHandler] = None) -> logging.Logger:
    """Create and return a colorized logger instance."""

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger # Prevent duplicate handlers

    logger.setLevel(level)

    if handler is None:
        handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = Formatter(
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
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def setup_discord_logger(bot: 'Bot') -> logging.Logger:
    """Setup a logger that sends errors to the Discord bot."""

    logger = get_logger("discord", level=logging.INFO, handler=DiscordHandler(bot))
    return logger