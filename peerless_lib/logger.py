# utils/logger.py
import logging

import colorlog

__all__ = (
    "get_logger",
)

def get_logger(name: str = "peerless", level: int = logging.INFO) -> logging.Logger:
    """Create and return a colorized logger instance."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger # Prevent duplicate handlers

    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = colorlog.ColoredFormatter(
        fmt="%(log_color)s[%(asctime)s][%(levelname)s] %(message)s",
        datefmt='%m/%d/%Y %I:%M:%S %p',
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger