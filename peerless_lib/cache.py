import asyncio
import json
from typing import Any, Dict, Iterable, Optional, Set, Tuple, Type, Union

from pydantic import BaseModel as PydanticBaseModel
from redis.asyncio.client import Redis
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .env import get_env
from .logger import get_logger
from .models import LeagueData, PlayerData, PlayerLeagueData

__all__ = (
    "Cache",
)

log = get_logger()

class Cache:
    def __init__(self) -> None:
        self.loop = asyncio.get_running_loop()

        self.redis: Redis

    async def connect(self) -> None:
        if hasattr(self, 'redis'):
            return
        
        self.redis = Redis.from_url(
            get_env("REDIS_URL"),
            decode_responses=True,
            health_check_interval=60,
            retry_on_timeout=True,
        )

        await self._verify_connection()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_not_exception_type((RuntimeError,))
    )
    async def _verify_connection(self) -> None:
        if not hasattr(self, 'redis'):
            raise RuntimeError("Redis client is not initialized. Please call connect() first.")
        
        try:
            await self.redis.ping()
            log.info("Connected to Redis")
        except Exception as e:
            log.error("Failed to connect to Redis")
            raise ConnectionError(f"Failed to connect to Redis: {e}") from e

    async def close(self) -> None:
        if hasattr(self, 'redis'):
            await self.redis.connection_pool.disconnect()
            await self.redis.close()
            log.info("Closed Redis connection")

    async def set(self, *path: str | int, model: Union[Dict[str, Any], PydanticBaseModel], nx: bool=False) -> None:
        name = ":".join([str(x) for x in path])
        data = model.model_dump_json() if isinstance(model, PydanticBaseModel) else json.dumps(model)

        await self.redis.set(name, data, ex=604800, nx=nx)
        log.debug(f"Cache set with key {name!r}")
    
    async def get[T](self, *path: str | int, model_cls: Type[T]) -> Optional[T]:
        name = ":".join([str(x) for x in path])
        item = await self.redis.get(name)

        if not item:
            log.debug(f"Cache missed with key {name!r}")
            return None
        
        log.debug(f"Cache hit with key {name!r}")
        
        data = json.loads(item)
        if issubclass(model_cls, PydanticBaseModel):
            return model_cls.model_validate(data)
        return model_cls(**data)
    
    async def delete(self, *paths: Union[Tuple[str], str]) -> None:
        keys = [":".join(map(str, path)) if isinstance(path, (list, tuple)) else path for path in paths]
        await self.redis.delete(*keys)
        log.info(f"Deleted keys {keys}")

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
        log.debug(f"Hash cache set with key {name!r}")

    async def hash_get[T: Union[LeagueData, PlayerData, PlayerLeagueData]](
        self, model_cls: Type[T], *, identifier: str, keys: Iterable[str]
    ) -> Tuple[Optional[T], Set[str]]:
        necessary_keys = {'league_id', 'player_id'} if issubclass(model_cls, PlayerLeagueData) else {'id'}
        necessary_keys.update(keys)

        name = f"{model_cls.__name__.lower()}:{identifier}"

        if not await self.redis.exists(name):
            log.debug(f"Hash cache missed with key {name!r}")
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

        log.debug(f"Hash cache hit with key {name!r} | retreived: {list(mapping.keys())}, missing: {unretrieved or ''}")
        return (model_cls.model_validate(mapping), unretrieved)