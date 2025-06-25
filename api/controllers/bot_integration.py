import json
from typing import Dict, Any, Optional
from litestar import Controller, Request, post, get
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

class BotIntegrationController(Controller):
    path = "/api/bot"

    async def verify_bot_token(self, request: Request) -> bool:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bot "):
            return False
        
        token = auth_header[4:]
        expected_token = request.app.state.get("bot_token")
        return token == expected_token

    @post("/settings/update")
    async def update_settings_from_bot(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.verify_bot_token(request):
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid bot token")
        
        guild_id = data.get("guild_id")
        settings = data.get("settings", {})
        
        if not guild_id:
            raise HTTPException(status_code=400, detail="guild_id required")
        
        db = request.app.state.db
        
        try:
            existing = await db.fetch_one(
                "SELECT settings FROM guild_settings WHERE guild_id = $1",
                guild_id
            )
            
            if existing:
                current_settings = existing["settings"] or {}
                current_settings.update(settings)
                
                await db.execute(
                    "UPDATE guild_settings SET settings = $1, updated_by = 'bot' WHERE guild_id = $2",
                    current_settings, guild_id
                )
            else:
                await db.execute(
                    "INSERT INTO guild_settings (guild_id, settings, updated_by) VALUES ($1, $2, 'bot')",
                    guild_id, settings
                )
            
            cache = request.app.state.cache
            if cache:
                await cache.set(f"guild_settings:{guild_id}", json.dumps(current_settings if existing else settings))
            
            return {"success": True, "message": "Settings updated from bot"}
            
        except Exception as e:
            print(f"Error updating settings from bot: {e}")
            raise HTTPException(status_code=500, detail="Failed to update settings")

    @get("/settings/{guild_id:str}")
    async def get_settings_for_bot(self, request: Request, guild_id: str) -> Dict[str, Any]:
        if not await self.verify_bot_token(request):
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid bot token")
        
        db = request.app.state.db
        cache = request.app.state.cache
        
        try:
            cached_settings = None
            if cache:
                cached_settings = await cache.get(f"guild_settings:{guild_id}")
                if cached_settings:
                    return {"settings": json.loads(cached_settings)}
            
            settings = await db.fetch_one(
                "SELECT settings FROM guild_settings WHERE guild_id = $1",
                guild_id
            )
            
            result = settings["settings"] if settings else {}
            
            if cache and not cached_settings:
                await cache.set(f"guild_settings:{guild_id}", json.dumps(result))
            
            return {"settings": result}
            
        except Exception as e:
            print(f"Error fetching settings for bot: {e}")
            return {"settings": {}}

    @post("/notify/setting_change")
    async def notify_setting_change(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        guild_id = data.get("guild_id")
        setting_key = data.get("setting_key")
        old_value = data.get("old_value")
        new_value = data.get("new_value")
        changed_by = data.get("changed_by", "website")
        
        if not guild_id or not setting_key:
            raise HTTPException(status_code=400, detail="guild_id and setting_key required")
        
        cache = request.app.state.cache
        if cache:
            notification = {
                "guild_id": guild_id,
                "setting_key": setting_key,
                "old_value": old_value,
                "new_value": new_value,
                "changed_by": changed_by,
                "timestamp": data.get("timestamp")
            }
            
            await cache.lpush(f"setting_changes:{guild_id}", json.dumps(notification))
            await cache.expire(f"setting_changes:{guild_id}", 86400)
        
        return {"success": True, "message": "Setting change notification sent"}

    @get("/health")
    async def health_check(self, request: Request) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "services": {
                "database": bool(request.app.state.get("db")),
                "cache": bool(request.app.state.get("cache"))
            }
        }

    @post("/validate/settings")
    async def validate_settings(self, request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.verify_bot_token(request):
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid bot token")
        
        settings = data.get("settings", {})
        errors = []
        
        validation_rules = {
            "roster_cap": {"type": "number", "min": 1, "max": 1000},
            "roster_minimum_amount": {"type": "number", "min": 0, "max": None},
            "roster_minimum_delay": {"type": "number", "min": 1, "max": 500},
            "roster_minimum_warnings": {"type": "number", "min": 0, "max": 10},
            "demand_amount": {"type": "number", "min": 0, "max": 10},
            "demand_cooldown": {"type": "number", "min": 1, "max": 500},
            "salary_cap": {"type": "number", "min": 1, "max": 999999999},
        }
        
        for key, value in settings.items():
            if key in validation_rules:
                rule = validation_rules[key]
                
                if rule["type"] == "number":
                    if not isinstance(value, (int, float)):
                        errors.append(f"{key}: must be a number")
                    elif rule["min"] is not None and value < rule["min"]:
                        errors.append(f"{key}: must be at least {rule['min']}")
                    elif rule["max"] is not None and value > rule["max"]:
                        errors.append(f"{key}: must be at most {rule['max']}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
