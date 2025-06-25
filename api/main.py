import importlib
import importlib.util
import sys
from pathlib import Path

from litestar import Controller, Litestar
from litestar.config.cors import CORSConfig

from utility import Cache, Database, get_logger
from utility.api import PeerlessState

logger = get_logger()

async def on_startup(app: Litestar) -> None:
    if not app.state.get("cache"):
        cache = Cache(endpoints_folder="api/endpoints", bot=None)
        app.state.cache = cache

    if not app.state.get("db"):
        db = Database(app.state.cache)
        app.state.db = db

    await app.state.cache.connect()
    await app.state.db.connect()

    load_controllers(app)
    for route in app.routes:
        print(route.path, route.methods)

def load_controllers(app: Litestar) -> None:
    path = Path('api/controllers').resolve()

    for file_path in path.rglob('*.py'):
        relative_path = file_path.relative_to(path.parent.parent).with_suffix('') # I hate that it has to be .parent.parent but it shouldnt change anytime soon
        module_path = ".".join(relative_path.parts)

        spec = importlib.util.find_spec(module_path)
        if not spec or not spec.loader:
            logger.warning(f"Unable to load module '{module_path}' for dynamic items")
            return

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_path] = module

        spec.loader.exec_module(module)

        for obj in module.__dict__.values():
            if not isinstance(obj, type):
                continue

            if issubclass(obj, Controller) and obj is not Controller:
                logger.info(f"Registering controller {obj.__name__!r} with path '{obj.path}'")
                app.register(obj)

async def on_shutdown(app: Litestar) -> None:
    if app.state.get("cache"):
        await app.state.cache.close()

    if app.state.get("db"):
        await app.state.db.close()

cors_config = CORSConfig(
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
)

app = Litestar(
    on_startup=[on_startup], 
    on_shutdown=[on_shutdown], 
    openapi_config={},  # type: ignore
    cors_config=cors_config,
    state=PeerlessState(state={
        "cache": None,
        "db": None,
    })
)