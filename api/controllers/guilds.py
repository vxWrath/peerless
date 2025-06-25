from typing import Dict, Any
from litestar import Controller, Request, get, patch
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

class GuildsController(Controller):
    path = "/api/guilds"

    async def check_guild_access(self, request: Request, guild_id: str) -> bool:
        access_token = request.session.get("access_token")
        if not access_token:
            return False
        
        user = request.session.get("user")
        if not user:
            return False
        
        import aiohttp
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}
            async with session.get("https://discord.com/api/users/@me/guilds", headers=headers) as resp:
                if resp.status != 200:
                    return False
                
                guilds = await resp.json()
        
        for guild in guilds:
            if guild["id"] == guild_id:
                permissions = int(guild.get("permissions", 0))
                return bool(permissions & 0x8)
        
        return False

    @get("/{guild_id:str}/settings")
    async def get_guild_settings(self, request: Request, guild_id: str) -> Dict[str, Any]:
        if not await self.check_guild_access(request, guild_id):
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
        
        db = request.app.state.db
        
        try:
            settings = await db.fetch_one(
                "SELECT settings FROM guild_settings WHERE guild_id = $1",
                guild_id
            )
            
            if settings:
                return settings["settings"] or {}
            else:
                return {}
                
        except Exception as e:
            print(f"Error fetching guild settings: {e}")
            return {}

    @patch("/{guild_id:str}/settings")
    async def update_guild_settings(self, request: Request, guild_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.check_guild_access(request, guild_id):
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")

        db = request.app.state.db
        cache = request.app.state.cache

        try:
            existing = await db.fetch_one(
                "SELECT settings FROM guild_settings WHERE guild_id = $1",
                guild_id
            )

            old_settings = existing["settings"] if existing else {}

            if existing:
                current_settings = existing["settings"] or {}
                current_settings.update(data)

                await db.execute(
                    "UPDATE guild_settings SET settings = $1, updated_by = 'website' WHERE guild_id = $2",
                    current_settings, guild_id
                )
            else:
                current_settings = data
                await db.execute(
                    "INSERT INTO guild_settings (guild_id, settings, updated_by) VALUES ($1, $2, 'website')",
                    guild_id, data
                )

            if cache:
                import json
                await cache.set(f"guild_settings:{guild_id}", json.dumps(current_settings))

                for key, new_value in data.items():
                    old_value = old_settings.get(key)
                    if old_value != new_value:
                        notification = {
                            "guild_id": guild_id,
                            "setting_key": key,
                            "old_value": old_value,
                            "new_value": new_value,
                            "changed_by": "website",
                            "timestamp": int(__import__('time').time())
                        }
                        await cache.lpush(f"setting_changes:{guild_id}", json.dumps(notification))
                        await cache.expire(f"setting_changes:{guild_id}", 86400)

            return {"message": "Settings updated successfully"}

        except Exception as e:
            print(f"Error updating guild settings: {e}")
            raise HTTPException(status_code=500, detail="Failed to update settings")
