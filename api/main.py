from pathlib import Path
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig

from api.controllers import account, bot

def create_app() -> Litestar:
    return Litestar(
        route_handlers=[account.AccountController, bot.BotController],
        template_config=TemplateConfig(
            directory=Path(__file__).parent / "templates",
            engine=JinjaTemplateEngine,
        ),
        cors_config=CORSConfig(
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            expose_headers=["*"]
        )
    )

app = create_app()
