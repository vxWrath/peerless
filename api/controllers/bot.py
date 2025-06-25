import os
from typing import Dict, Any

import aiohttp
from litestar import get
from litestar.controller import Controller


class BotController(Controller):
    path = "/bot"

    @get("/application")
    async def get_application_info(self) -> Dict[str, Any]:
        client_id = os.environ.get("DISCORD_CLIENT_ID")
        if client_id:
            return {"id": client_id}
        
        try:
            token = os.environ.get("TOKEN")
            if not token:
                return {"error": "No Discord token or client ID configured"}
            
            headers = {"Authorization": f"Bot {token}"}
            async with aiohttp.ClientSession() as session:
                async with session.get("https://discord.com/api/v10/oauth2/applications/@me", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"id": data.get("id")}
                    else:
                        return {"error": f"Failed to fetch application info: {response.status}"}
        except Exception as e:
            return {"error": f"Failed to get application info: {str(e)}"}
