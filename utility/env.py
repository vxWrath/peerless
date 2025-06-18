import os
import sys
from typing import Optional

from .logger import get_logger

__all__ = (
    'get_env',
)

logger = get_logger()

def get_env(name: str, default: Optional[str]=None) -> str:
    value = os.getenv(key=name, default=default)

    if value is None:
        logger.error(f"Environment variable '{name}' is not set.")
        sys.exit(1)
        
    return value