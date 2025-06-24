from typing import Dict

from litestar import get
from litestar.controller import Controller


class AccountController(Controller):
    path = "/account"

    @get("/")
    async def account_home(self) -> Dict[str, str]:
        return {"message": "You are now logged in!"}

    @get("/{account_id:int}")
    async def account_id(self, account_id: int) -> Dict[str, int | str]:
        return {"id": account_id, "name": f"Account {account_id}"}
