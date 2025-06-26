from typing import Any, Dict, Optional

from discord import Permissions
from discord.utils import oauth_url
from litestar import Request, get
from litestar.controller import Controller
from litestar.exceptions import NotAuthorizedException

from utility import get_env
from utility.api import OAuthState, PeerlessState

CLIENT_ID = get_env("CLIENT_ID")
CLIENT_SECRET = get_env("CLIENT_SECRET")
FRONTEND_URL = get_env("FRONTEND_URL")
API_SECRET = get_env("API_SECRET")

class BotController(Controller):
    path = "/bot"

    @get("/info")
    async def get_bot_info(self, request: Request) -> Dict[str, Any]:
        if request.headers.get("Authorization") != API_SECRET:
            raise NotAuthorizedException(detail="Invalid API secret.")
        return {}

    @get("/oauth")
    async def get_oauth_url(self, state: PeerlessState, request: Request, redirect_to: Optional[str]) -> Dict[str, str]:
        if request.headers.get("Authorization") != API_SECRET:
            raise NotAuthorizedException(detail="Invalid API secret.")
        
        redirect_to = redirect_to or "/servers"
        
        oauth_state = OAuthState(redirect_to=redirect_to)
        await state.cache.set_oauth_state(oauth_state)

        return {"url": oauth_url(
            client_id=CLIENT_ID,
            permissions=Permissions(),
            redirect_uri=f"{FRONTEND_URL.replace('frontend', 'localhost')}/auth/callback",
            scopes=["identify", "guilds"],
            state=oauth_state.token
        )}