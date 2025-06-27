import json

from litestar import Request, get
from litestar.controller import Controller

from utility.api import DiscordUser, PeerlessState, require_user


class UserController(Controller):
    path = "/api/user"

    @get("/", guards=[require_user])
    async def get_user(self, request: Request[DiscordUser, None, PeerlessState]) -> DiscordUser:
        print(json.dumps(request.user.model_dump(mode="json"), indent=4), flush=True)
        return request.user
    
    @get("/<int:user_id>", guards=[require_user])
    async def get_user_by_id(self, request: Request[DiscordUser, None, PeerlessState], user_id: int) -> DiscordUser:
        return {}