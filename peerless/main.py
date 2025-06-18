import asyncio

from utility import Cache, get_logger

logger = get_logger()

async def main():
    cache = Cache()

    await cache.connect()
    cache.load_endpoints('peerless/ipc')

    await cache._task

    await cache.close()

asyncio.run(main())