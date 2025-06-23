# very basic setup app
from litestar import Litestar, get


@get("/")
def hello_world() -> dict:
    return {"message": "Hello from Litestar!"}

app = Litestar(route_handlers=[hello_world])