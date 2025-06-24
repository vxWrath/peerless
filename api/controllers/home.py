from typing import Dict

from litestar import get
from litestar.controller import Controller


class HomeController(Controller):
    path = "/"

    @get("/")
    async def home(self) -> Dict[str, str]:
        return {"message": "Hello from Peerless!"}