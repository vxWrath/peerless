from typing import Any, Dict, Optional

from aiohttp import FormData as AIOHTTPFormData
from discord import Permissions
from discord.utils import oauth_url
from litestar import Request, get
from litestar.controller import Controller
from litestar.exceptions import (
    InternalServerException,
    NotAuthorizedException,
    ValidationException,
)

from utility import get_env, get_logger
from utility.api import (
    DiscordPartialGuild,
    DiscordUser,
    OAuthState,
    PeerlessState,
    require_user,
)

logger = get_logger()

CLIENT_ID = get_env("CLIENT_ID")
CLIENT_SECRET = get_env("CLIENT_SECRET")
FRONTEND_URL = get_env("FRONTEND_URL")

class OAuthController(Controller):
    path = "/oauth"

    @get("/url")
    async def get_oauth_url(self, state: PeerlessState, request: Request, redirect_to: Optional[str]) -> Dict[str, str]:
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
    
    @get("/code")
    async def get_oauth_code(self, state: PeerlessState, request: Request, code: Optional[str], oauth_token: Optional[str]) -> Dict[str, Any]:
        if not code:
            raise ValidationException(detail="Code parameter is required.")

        if not oauth_token:
            raise ValidationException(detail="OAuth token parameter is required.")

        oauth_state = await state.cache.get_oauth_state(oauth_token)
        if not oauth_state:
            raise NotAuthorizedException(detail="No OAuth state found.")
        
        await state.cache.delete_oauth_state(oauth_token)

        form_data = AIOHTTPFormData()
        form_data.add_field("client_id", CLIENT_ID)
        form_data.add_field("client_secret", CLIENT_SECRET)
        form_data.add_field("code", code)
        form_data.add_field("grant_type", "authorization_code")
        form_data.add_field("redirect_uri", f"{FRONTEND_URL.replace('frontend', 'localhost')}/auth/callback")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            req = await state.http_client.post(
                url="https://discord.com/api/oauth2/token",
                headers=headers,
                data=form_data,
            )
            raw_data = await req.json()
        except Exception as e:
            logger.error(f"Error occurred while exchanging OAuth code: {e}")
            raise InternalServerException(detail="Failed to exchange OAuth code.")

        if "access_token" not in raw_data:
            logger.error(f"Unexpected response from Discord API: {raw_data}")
            raise InternalServerException(detail="Failed to exchange OAuth code.")

        headers = {
            "Authorization": f"Bearer {raw_data['access_token']}",
        }

        try:
            req = await state.http_client.get(
                url="https://discord.com/api/users/@me",
                headers=headers,
            )
            user = DiscordUser.model_validate(await req.json())
        except Exception as e:
            logger.error(f"Error occurred while fetching user info: {e}")
            raise InternalServerException(detail="Failed to fetch user info.")

        try:
            req = await state.http_client.get(
                url="https://discord.com/api/users/@me/guilds",
                headers=headers,
            )
            guilds = {
                int(guild['id']): DiscordPartialGuild.model_validate(guild) for guild in await req.json()
            }
        except Exception as e:
            logger.error(f"Error occurred while fetching user guilds: {e}")
            raise InternalServerException(detail="Failed to fetch user guilds.")
        
        user.guilds = guilds
        await state.cache.set_website_user(user)

        return {
            "user": user.model_dump(mode='json'),
            "redirect_to": oauth_state.redirect_to,
        }

    @get("/logout", guards=[require_user])
    async def logout(self, state: PeerlessState, request: Request[DiscordUser, None, PeerlessState]) -> Dict[str, str]:
        await state.cache.delete_website_user(request.user.session_token)
        return {"detail": "Logged out successfully."}