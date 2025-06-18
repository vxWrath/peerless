import json
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Union
from uuid import uuid4

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_validator

if TYPE_CHECKING:
    from .cache import Cache

__all__ = (
    "ReturnWhen",
    "RedisMessage",
    "RedisRequest",
    "RedisResponse",
    "RedisCommand",
)

class ReturnWhen(Enum):
    FIRST = 'first'
    ALL = 'all'

# These classes may need to be switched from pydantic to msgspec in the future
# msgspec.Struct is more efficient than pydantic.BaseModel

class RedisMessage(PydanticBaseModel):
    type: str
    pattern: Optional[str]
    channel: str
    data: Union[int, Dict[str, Any]]

    @field_validator('data', mode='before')
    @classmethod
    def wrap_data(cls, data: int | str, handler: Any):
        if isinstance(data, str):
            return json.loads(data)
        return data

class RedisRequest(PydanticBaseModel):
    nonce: str = Field(default_factory=lambda : str(uuid4()))
    data: Dict[str, Any]

class RedisResponse(PydanticBaseModel):
    data: Optional[Dict[str, Any]]

class RedisCommand[T: PydanticBaseModel]:
    CHANNEL: str
    MODEL: T

    def __init__(self, cache: 'Cache') -> None:
        self.cache = cache

    async def handle(self, context: T) -> Optional[Dict[str, Any]]:
        raise NotImplementedError()