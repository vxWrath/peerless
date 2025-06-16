import asyncio
import json
import os
from typing import Any, Dict, Iterable, Optional, Set, Tuple, Type, Union

from pydantic import BaseModel as PydanticBaseModel
from redis.asyncio.client import Redis

from .models import LeagueData, PlayerData, PlayerLeagueData

__all__ = (
    "Cache",
)

class Cache:
    def __init__(self) -> None:
        self.loop = asyncio.get_running_loop()

        self.redis: Redis

    async def connect(self) -> None:
        self.redis = Redis.from_url(
            os.getenv("REDIS_URL", ""), 
            decode_responses=True,
            health_check_interval=60,
            retry_on_timeout=True,
        )
        await self.redis.initialize()

    async def close(self) -> None:
        if hasattr(self, 'redis'):
            await self.redis.close()
            await self.redis.connection_pool.disconnect()

    async def set(self, *path: str | int, model: Union[Dict[str, Any], PydanticBaseModel], nx: bool=False) -> bool:
        name = ":".join([str(x) for x in path])
        data = model.model_dump() if isinstance(model, PydanticBaseModel) else model

        res = await self.redis.set(name, json.dumps(data), ex=604800, nx=nx)

        if res:
            return True
        return False
    
    async def get[T](self, *path: str | int, model_cls: Type[T]) -> Optional[T]:
        name = ":".join([str(x) for x in path])
        item = await self.redis.get(name)

        if not item:
            return None
        
        data = json.loads(item)
        if isinstance(model_cls, PydanticBaseModel):
            return model_cls.model_validate(data)
        return model_cls(**data)
    
    async def delete(self, *paths: Union[Tuple[str], str]) -> None:
        await self.redis.delete(*[":".join(map(str, path)) if isinstance(path, (list, tuple)) else path for path in paths])

    async def hash_set(self, model: Union[LeagueData, PlayerData, PlayerLeagueData], *, identifier: str, keys: Iterable[str]) -> None:
        necessary_keys = {'league_id', 'player_id'} if isinstance(model, PlayerLeagueData) else {'id'}
        necessary_keys.update(keys)

        name = f"{model.__class__.__name__.lower()}:{identifier}"
        dump = model.model_dump(mode="json", include=necessary_keys)

        await self.redis.hset(name, mapping={
            k: json.dumps(v)
            for k, v in dump.items()
        }) # type: ignore
        await self.redis.hexpire(name, 3600, *necessary_keys)

    async def hash_get[T: Union[LeagueData, PlayerData, PlayerLeagueData]](
        self, model_cls: Type[T], *, identifier: str, keys: Iterable[str]
    ) -> Tuple[Optional[T], Set[str]]:
        necessary_keys = {'league_id', 'player_id'} if issubclass(model_cls, PlayerLeagueData) else {'id'}
        necessary_keys.update(keys)

        name = f"{model_cls.__name__.lower()}:{identifier}"

        if not await self.redis.exists(name):
            return (None, necessary_keys)
        
        necessary_keys = list(necessary_keys)
        data = await self.redis.hmget(name, necessary_keys) # type: ignore

        mapping: Dict[str, Any] = {}
        unretrieved: Set[str] = set()

        for i, key in enumerate(necessary_keys):
            if data[i] is not None:
                mapping[key] = json.loads(data[i])
            else:
                unretrieved.add(key)

        return (model_cls.model_validate(mapping, strict=True), unretrieved)