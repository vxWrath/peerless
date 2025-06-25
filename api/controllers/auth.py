import os
import secrets
from typing import Optional
from urllib.parse import urlencode

import aiohttp
from litestar import Controller, Request, Response, get, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_302_FOUND, HTTP_401_UNAUTHORIZED

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8000/api/auth/callback")

class AuthController(Controller):
    path = "/api/auth"

    @get("/discord")
    async def discord_login(self, request: Request) -> Response:
        state = secrets.token_urlsafe(32)
        request.session["oauth_state"] = state
        
        params = {
            "client_id": DISCORD_CLIENT_ID,
            "redirect_uri": DISCORD_REDIRECT_URI,
            "response_type": "code",
            "scope": "identify guilds",
            "state": state,
        }
        
        discord_url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
        return Response(None, status_code=HTTP_302_FOUND, headers={"Location": discord_url})

    @get("/callback")
    async def discord_callback(self, request: Request) -> Response:
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        
        if not code or not state:
            raise HTTPException(status_code=400, detail="Missing code or state")
        
        if state != request.session.get("oauth_state"):
            raise HTTPException(status_code=400, detail="Invalid state")
        
        async with aiohttp.ClientSession() as session:
            token_data = {
                "client_id": DISCORD_CLIENT_ID,
                "client_secret": DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": DISCORD_REDIRECT_URI,
            }
            
            async with session.post("https://discord.com/api/oauth2/token", data=token_data) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to get access token")
                
                token_response = await resp.json()
                access_token = token_response["access_token"]
            
            headers = {"Authorization": f"Bearer {access_token}"}
            async with session.get("https://discord.com/api/users/@me", headers=headers) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to get user info")
                
                user_data = await resp.json()
        
        request.session["user"] = user_data
        request.session["access_token"] = access_token
        
        return Response(None, status_code=HTTP_302_FOUND, headers={"Location": "http://localhost:5173/dashboard"})

    @get("/me")
    async def get_current_user(self, request: Request) -> dict:
        user = request.session.get("user")
        if not user:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        return user

    @get("/guilds")
    async def get_user_guilds(self, request: Request) -> list:
        access_token = request.session.get("access_token")
        if not access_token:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}
            async with session.get("https://discord.com/api/users/@me/guilds", headers=headers) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to get guilds")
                
                guilds = await resp.json()
        
        admin_guilds = []
        for guild in guilds:
            permissions = int(guild.get("permissions", 0))
            if permissions & 0x8:
                admin_guilds.append(guild)
        
        return admin_guilds

    @post("/logout")
    async def logout(self, request: Request) -> dict:
        request.session.clear()
        return {"message": "Logged out successfully"}
