import asyncio

from utility import Cache, ReturnWhen, get_logger

logger = get_logger()

async def main():
    cache = Cache()

    await cache.connect()
    cache.load_endpoints('dashboard/ipc')
    
    resp = await cache.send_message("test", {"message": "Hello, World!"}, return_when=ReturnWhen.FIRST)
    print(resp, flush=True)

    await cache.close()

asyncio.run(main())