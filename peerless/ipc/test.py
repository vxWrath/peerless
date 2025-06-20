from typing import Any, Dict, Optional

from pydantic import BaseModel

from utility import RedisCommand, get_logger

logger = get_logger()

class TestMessage(BaseModel):
    message: str

class TestCommand(RedisCommand):
    CHANNEL = 'test'
    MODEL = TestMessage

    async def handle(self, context: TestMessage) -> Optional[Dict[str, Any]]:
        logger.debug(f"Received message: {context.message}")
        return {"status": "success"}