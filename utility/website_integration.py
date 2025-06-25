import aiohttp
import json
import os
from typing import Dict, Any, Optional

class WebsiteIntegration:
    def __init__(self, api_base_url: str = "http://localhost:8000", bot_token: str = None):
        self.api_base_url = api_base_url
        self.bot_token = bot_token or os.getenv("BOT_TOKEN")
        self.headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json"
        }

    async def get_guild_settings(self, guild_id: str) -> Dict[str, Any]:
        """Get guild settings from website"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/api/bot/settings/{guild_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("settings", {})
                    return {}
        except Exception as e:
            print(f"Error fetching guild settings: {e}")
            return {}

    async def update_guild_settings(self, guild_id: str, settings: Dict[str, Any]) -> bool:
        """Update guild settings from bot"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "guild_id": guild_id,
                    "settings": settings
                }
                async with session.post(
                    f"{self.api_base_url}/api/bot/settings/update",
                    headers=self.headers,
                    json=payload
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error updating guild settings: {e}")
            return False

    async def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate settings against website rules"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"settings": settings}
                async with session.post(
                    f"{self.api_base_url}/api/bot/validate/settings",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return {"valid": False, "errors": ["Validation service unavailable"]}
        except Exception as e:
            print(f"Error validating settings: {e}")
            return {"valid": False, "errors": [str(e)]}

    async def notify_setting_change(self, guild_id: str, setting_key: str, old_value: Any, new_value: Any) -> bool:
        """Notify website of setting change from bot"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "guild_id": guild_id,
                    "setting_key": setting_key,
                    "old_value": old_value,
                    "new_value": new_value,
                    "changed_by": "bot",
                    "timestamp": int(__import__('time').time())
                }
                async with session.post(
                    f"{self.api_base_url}/api/bot/notify/setting_change",
                    headers=self.headers,
                    json=payload
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Error notifying setting change: {e}")
            return False

    async def sync_critical_settings(self, guild_id: str) -> Dict[str, Any]:
        """Sync critical settings that affect bot behavior"""
        settings = await self.get_guild_settings(guild_id)
        
        critical_settings = {
            "roster_cap": settings.get("roster_cap", 20),
            "transactions_status": settings.get("transactions_status", True),
            "alerts": settings.get("alerts"),
            "timezone": settings.get("timezone", "America/New_York"),
            "operations_roles": settings.get("operations_roles", {}),
            "free_agent_roles": settings.get("free_agent_roles"),
            "suspended_roles": settings.get("suspended_roles")
        }
        
        return critical_settings

    async def check_health(self) -> bool:
        """Check if website API is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base_url}/api/bot/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("status") == "healthy"
                    return False
        except Exception:
            return False

class SettingsManager:
    def __init__(self, bot, website_integration: WebsiteIntegration):
        self.bot = bot
        self.website = website_integration
        self._cached_settings = {}

    async def get_setting(self, guild_id: str, key: str, default: Any = None) -> Any:
        """Get a specific setting for a guild"""
        if guild_id not in self._cached_settings:
            await self.refresh_settings(guild_id)
        
        return self._cached_settings.get(guild_id, {}).get(key, default)

    async def set_setting(self, guild_id: str, key: str, value: Any) -> bool:
        """Set a specific setting for a guild"""
        old_value = await self.get_setting(guild_id, key)
        
        validation = await self.website.validate_settings({key: value})
        if not validation.get("valid", False):
            print(f"Setting validation failed: {validation.get('errors', [])}")
            return False
        
        success = await self.website.update_guild_settings(guild_id, {key: value})
        if success:
            if guild_id not in self._cached_settings:
                self._cached_settings[guild_id] = {}
            self._cached_settings[guild_id][key] = value
            
            await self.website.notify_setting_change(guild_id, key, old_value, value)
        
        return success

    async def refresh_settings(self, guild_id: str) -> None:
        """Refresh cached settings for a guild"""
        settings = await self.website.get_guild_settings(guild_id)
        self._cached_settings[guild_id] = settings

    async def get_roster_cap(self, guild_id: str) -> int:
        """Get roster cap for a guild"""
        return await self.get_setting(guild_id, "roster_cap", 20)

    async def is_transactions_enabled(self, guild_id: str) -> bool:
        """Check if transactions are enabled for a guild"""
        return await self.get_setting(guild_id, "transactions_status", True)

    async def get_alerts_channel(self, guild_id: str) -> Optional[str]:
        """Get alerts channel for a guild"""
        return await self.get_setting(guild_id, "alerts")

    async def get_timezone(self, guild_id: str) -> str:
        """Get timezone for a guild"""
        return await self.get_setting(guild_id, "timezone", "America/New_York")
