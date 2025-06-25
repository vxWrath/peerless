import json
import os
import urllib.parse
import json
from typing import Dict, Any

import aiohttp
from litestar import get, post
from litestar.controller import Controller
from litestar.response import Redirect
from litestar.connection import Request
from redis.asyncio import Redis

client_secret = os.environ.get("DISCORD_CLIENT_SECRET")

redis_url = os.environ.get("REDIS_URL", "redis://redis:6379")
redis_client = Redis.from_url(redis_url, decode_responses=True)

class AccountController(Controller):
    path = "/account"

    def _get_frontend_url(self, request: Request) -> str:
        frontend_host = os.environ.get("FRONTEND_HOST", "localhost:5173")
        scheme = "https" if request.url.scheme == "https" else "http"
        return f"{scheme}://{frontend_host}"

    def _get_api_base_url(self, request: Request) -> str:
        api_host = os.environ.get("API_HOST", "localhost:8000")
        scheme = "https" if request.url.scheme == "https" else "http"
        return f"{scheme}://{api_host}"

    async def _get_client_id(self) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://api:8000/bot/application") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("id")
        except Exception as e:
            print(f"Failed to get client ID from bot: {e}")

        return os.environ.get("DISCORD_CLIENT_ID", "")
    
    @get("/login/discord")
    async def login_discord(self, request: Request) -> Redirect:
        print("login_discord route called")

        if not client_secret:
            return Redirect(path=f"{self._get_frontend_url(request)}/?error=Discord client secret not configured")

        client_id = await self._get_client_id()
        if not client_id:
            return Redirect(path=f"{self._get_frontend_url(request)}/?error=Discord client not configured")

        api_base_url = self._get_api_base_url(request)
        redirect_uri = urllib.parse.quote_plus(f"{api_base_url}/account/callback/discord")
        discord_url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=identify"
        return Redirect(path=discord_url)
    
    @get("/callback/discord")
    async def callback_discord(self, code: str, request: Request) -> Redirect:
        print("callback_discord route called")

        if not client_secret:
            return Redirect(path=f"{self._get_frontend_url(request)}/?error=Discord client secret not configured")

        client_id = await self._get_client_id()
        frontend_url = self._get_frontend_url(request)

        if not client_id:
            return Redirect(path=f"{frontend_url}/?error=Discord client not configured")

        token_url = "https://discord.com/api/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"{self._get_api_base_url(request)}/account/callback/discord",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, headers=headers, data=data) as response:
                token_data = await response.json()

        access_token = token_data.get("access_token")

        if not access_token:
            error_url = f"{frontend_url}/?error=Failed to retrieve access token"
            return Redirect(path=error_url)

        user_url = "https://discord.com/api/users/@me"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(user_url, headers=headers) as response:
                user_data = await response.json()

        username = user_data.get("username")
        discord_id = user_data.get("id")
        avatar = user_data.get("avatar")

        avatar_url = None
        if avatar:
            avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar}.png"
        else:
            default_avatar = int(discord_id) % 5
            avatar_url = f"https://cdn.discordapp.com/embed/avatars/{default_avatar}.png"

        user_data = {
            "username": username,
            "discord_id": discord_id,
            "avatar_url": avatar_url
        }

        await redis_client.setex(f"user:{discord_id}", 86400, json.dumps(user_data))

        redirect_url = f"{frontend_url}/?username={urllib.parse.quote(username)}&discord_id={discord_id}&avatar_url={urllib.parse.quote(avatar_url)}"
        return Redirect(path=redirect_url)

    @get("/user/{discord_id:str}")
    async def get_user(self, discord_id: str) -> Dict[str, Any]:
        user_data = await redis_client.get(f"user:{discord_id}")
        if user_data:
            return json.loads(user_data)
        return {"error": "User not found"}

    @post("/user")
    async def store_user(self, data: Dict[str, Any]) -> Dict[str, str]:
        discord_id = data.get("discord_id")
        if not discord_id:
            return {"error": "discord_id is required"}

        await redis_client.setex(f"user:{discord_id}", 86400, json.dumps(data))
        return {"message": "User data stored successfully"}

    @get("/logout")
    async def logout(self, request: Request) -> Redirect:
        return Redirect(path=self._get_frontend_url(request))
