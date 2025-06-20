import asyncio
import importlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, Generic, Iterable, List, Optional, Set, Tuple, Type, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidationError
from redis.asyncio.client import PubSub, Redis
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .bot import BotT
from .env import get_env
from .ipcmodels import (
    RedisCommand,
    RedisMessage,
    RedisRequest,
    RedisResponse,
    ReturnWhen,
)
from .logger import get_logger
from .models import LeagueData, PlayerData, PlayerLeagueData
from .utils import create_logged_task

__all__ = (
    "Cache",
)

logger = get_logger("cache")

class Cache(Generic[BotT]):
    def __init__(self, bot: BotT) -> None:
        self.loop = asyncio.get_running_loop()
        self.bot  = bot

        self.responses: Dict[str, List[RedisResponse]] = {}
        self.futures: Dict[str, asyncio.Future[RedisResponse]] = {}
        self.endpoints: List[RedisCommand[PydanticBaseModel]] = []

        self.redis: Redis
        self.pubsub: PubSub
        self._task: asyncio.Task[None]

    async def connect(self) -> None:
        if hasattr(self, 'redis'):
            return
        
        self.redis = Redis.from_url(
            get_env("REDIS_URL"),
            decode_responses=True,
            health_check_interval=60,
            retry_on_timeout=True,
        )
        self.pubsub = self.redis.pubsub()

        await self._verify_connection()
        self._task = create_logged_task(self.listen())

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
            await self.pubsub.ping()

            logger.info("Connected to Redis")
        except Exception as e:
            logger.error("Failed to connect to Redis")
            raise ConnectionError(f"Failed to connect to Redis: {e}") from e

    async def close(self) -> None:
        if hasattr(self, 'redis'):
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
            
            await self.redis.connection_pool.disconnect()
            await self.redis.close()

            logger.info("Closed Redis connection")

    def load_endpoints(self, folder_path: str) -> None:
        path = Path(folder_path).resolve()

        for file_path in path.rglob('*.py'):
            relative_path = file_path.relative_to(path.parent).with_suffix('')
            module_path = ".".join(relative_path.parts)

            spec = importlib.util.find_spec(module_path)
            if not spec:
                raise FileNotFoundError(f"Couldn't find '{module_path}'")
            
            if not spec.loader:
                # No idea what spec.loader is, but I don't think it will ever be None
                # This is just to satisfy the type checker
                raise ImportError(f"Module '{module_path}' has no loader")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            commands: List[Type[RedisCommand[PydanticBaseModel]]] = [
                obj for obj in module.__dict__.values() if isinstance(obj, type) and issubclass(obj, RedisCommand) and obj is not RedisCommand
            ]

            for cmd in commands:
                logger.debug(f"Registered command {cmd.__name__!r} with channel {cmd.CHANNEL!r}")
                self.endpoints.append(cmd(self))

    async def listen(self) -> None:
        channels = [x.CHANNEL for x in self.endpoints]
        if channels:
            await self.pubsub.subscribe(*channels)

        while True:
            message_data = await self.pubsub.get_message(ignore_subscribe_messages=True)

            if message_data is None:
                await asyncio.sleep(0.1)
                continue
            
            try:
                message = RedisMessage.model_validate(message_data)
            except ValidationError as e:
                continue  # Skip messages that don't match the expected format
            except Exception as e:
                logger.error(f"Failed to parse message: {e}")
                continue
            
            if 'reply' in message.channel.lower():
                resp = RedisResponse.model_validate(message.data)

                if message.channel in self.responses:
                    logger.debug(f"Responded to reply for {message.channel!r}")
                    self.responses[message.channel].append(resp)
                elif message.channel in self.futures:
                    logger.debug(f"Responded to reply for {message.channel!r}")
                    future = self.futures.pop(message.channel)
                    future.set_result(resp)
            else:
                create_logged_task(self.handle(message))

    async def handle(self, message: RedisMessage) -> None:
        request = RedisRequest.model_validate(message.data)
        command = next((x for x in self.endpoints if x.CHANNEL == message.channel), None)

        if command:
            logger.debug(f"Handling command for channel {message.channel!r}")
            response_data = await command.handle(command.MODEL.model_validate(request.data))
            response = RedisResponse(data=response_data)
        else:
            response = RedisResponse(data=None)

        await self.redis.publish(
            channel = f"reply:{request.nonce}",
            message = response.model_dump_json()
        )
        logger.debug(f"Sent response for {message.channel!r}")

    async def send_message(self, channel: str, data: Dict[str, Any], wait_for: float=1.5, return_when: ReturnWhen=ReturnWhen.ALL) -> List[RedisResponse]:
        request = RedisRequest(data=data)

        await self.pubsub.subscribe(f"reply:{request.nonce}")
        await self.redis.publish(
            channel = channel,
            message = request.model_dump_json()
        )

        if return_when == ReturnWhen.FIRST:
            return [await self.wait_for_reply(request, timeout=wait_for)]
        return await self.wait_for_replies(request, wait_for=wait_for)
    
    async def wait_for_replies(self, request: RedisRequest, wait_for: float) -> List[RedisResponse]:
        self.responses[f"reply:{request.nonce}"] = []

        await asyncio.sleep(wait_for)
        responses = self.responses[f"reply:{request.nonce}"]

        self.responses.pop(f"reply:{request.nonce}")
        await self.pubsub.unsubscribe(f"reply:{request.nonce}")

        return responses
    
    async def wait_for_reply(self, request: RedisRequest, timeout: float) -> RedisResponse:
        future: asyncio.Future[RedisResponse] = self.loop.create_future()
        self.futures[f"reply:{request.nonce}"] = future

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.futures.pop(f"reply:{request.nonce}")
            return RedisResponse(data=None)
        finally:
            future.cancel()
            await self.pubsub.unsubscribe(f"reply:{request.nonce}")

    async def set(self, *path: str | int, model: Union[Dict[str, Any], PydanticBaseModel], nx: bool=False) -> None:
        name = ":".join([str(x) for x in path])
        data = model.model_dump_json() if isinstance(model, PydanticBaseModel) else json.dumps(model)

        await self.redis.set(name, data, ex=604800, nx=nx)
        logger.debug(f"Cache set with key {name!r}")
    
    async def get[T](self, *path: str | int, model_cls: Type[T]) -> Optional[T]:
        name = ":".join([str(x) for x in path])
        item = await self.redis.get(name)

        if not item:
            logger.debug(f"Cache missed with key {name!r}")
            return None
        
        logger.debug(f"Cache hit with key {name!r}")
        
        data = json.loads(item)
        if issubclass(model_cls, PydanticBaseModel):
            return model_cls.model_validate(data)
        return model_cls(**data)
    
    async def delete(self, *paths: Union[Tuple[str], str]) -> None:
        keys = [":".join(map(str, path)) if isinstance(path, (list, tuple)) else path for path in paths]
        await self.redis.delete(*keys)
        logger.debug(f"Deleted keys {keys}")

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
        logger.debug(f"Hash cache set with key {name!r}")

    async def hash_get[T: Union[LeagueData, PlayerData, PlayerLeagueData]](
        self, model_cls: Type[T], *, identifier: str, keys: Iterable[str]
    ) -> Tuple[Optional[T], Set[str]]:
        necessary_keys = {'league_id', 'player_id'} if issubclass(model_cls, PlayerLeagueData) else {'id'}
        necessary_keys.update(keys)

        name = f"{model_cls.__name__.lower()}:{identifier}"

        if not await self.redis.exists(name):
            logger.debug(f"Hash cache missed with key {name!r}")
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

        logger.debug(f"Hash cache hit with key {name!r} | retrieved: {list(mapping.keys())}, missing: {unretrieved or ''}")
        return (model_cls.model_validate(mapping), unretrieved)