from typing import TYPE_CHECKING, Optional

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import BaseRouteHandler

from ..env import get_env
from ..logger import get_logger

if TYPE_CHECKING:
    from .models import DiscordUser
    from .state import PeerlessState

__all__ = ("require_secret", "require_user")

logger = get_logger()
API_SECRET = get_env("API_SECRET")

def require_secret(connection: ASGIConnection[BaseRouteHandler, None, None, 'PeerlessState'], _: BaseRouteHandler) -> None:
    if connection.headers.get("Authorization") != API_SECRET:
        raise NotAuthorizedException(detail="Invalid API secret.")

async def require_user(connection: ASGIConnection[BaseRouteHandler, None, None, 'PeerlessState'], _: BaseRouteHandler) -> None:
    session_token = connection.headers.get("X-Session-Token")

    if not session_token:
        raise NotAuthorizedException(detail="Session token is required.")

    user: Optional['DiscordUser'] = await connection.app.state.cache.get_website_user(session_token)

    if not user:
        raise NotAuthorizedException(detail="User not found or session expired.")
    
    connection.scope["user"] = user