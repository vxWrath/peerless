import asyncio

from utility import Cache, ReturnWhen, get_logger

logger = get_logger()

async def main():
    cache = Cache(endpoints_folder='dashboard/ipc', bot=None)

    await cache.connect()

    resp = await cache.send_message("test", {"message": "Hello, World!"}, return_when=ReturnWhen.FIRST)
    print(resp, flush=True)

    await cache.close()

asyncio.run(main())