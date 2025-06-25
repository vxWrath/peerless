import pytest
from httpx import AsyncClient
from litestar import Litestar
from litestar.testing import AsyncTestClient
from api.controllers.home import HomeController
from api.controllers.account import AccountController

class TestHomeController:
    @pytest.fixture
    def app(self):
        return Litestar(route_handlers=[HomeController])

    @pytest.mark.asyncio
    async def test_home_endpoint(self, app):
        async with AsyncTestClient(app=app) as client:
            response = await client.get("/")
            assert response.status_code == 200
            assert response.json() == {"message": "Hello from Peerless!"}

class TestAccountController:
    @pytest.fixture
    def app(self):
        return Litestar(route_handlers=[AccountController])

    @pytest.mark.asyncio
    async def test_account_home(self, app):
        async with AsyncTestClient(app=app) as client:
            response = await client.get("/account/")
            assert response.status_code == 200
            assert response.json() == {"message": "You are now logged in!"}

    @pytest.mark.asyncio
    async def test_account_id(self, app):
        async with AsyncTestClient(app=app) as client:
            account_id = 123
            response = await client.get(f"/account/{account_id}")
            assert response.status_code == 200
            expected = {"id": account_id, "name": f"Account {account_id}"}
            assert response.json() == expected

    @pytest.mark.asyncio
    async def test_account_id_invalid(self, app):
        async with AsyncTestClient(app=app) as client:
            response = await client.get("/account/invalid")
            assert response.status_code == 404
