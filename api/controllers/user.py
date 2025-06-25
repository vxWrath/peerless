from litestar import Request, get
from litestar.controller import Controller
from litestar.exceptions import NotAuthorizedException

from utility.api import DiscordUser, PeerlessState


class UserController(Controller):
    path = "/api/user"

    @get("/")
    async def get_user(self, request: Request, state: PeerlessState) -> DiscordUser:
        session_token = request.cookies.get("session")
        if not session_token:
            raise NotAuthorizedException(detail="Missing auth cookies.")

        user = await state.cache.get_website_user(session_token)
        if not user:
            raise NotAuthorizedException(detail="Invalid auth cookies.")

        return user