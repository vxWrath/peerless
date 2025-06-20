import asyncio
import signal
import sys

print(sys.path, flush=True)

from utility import Bot, Cache, Database, get_env, get_logger, setup_discord_logger

logger = get_logger("peerless")
shutdown_event = asyncio.Event()

def shutdown():
    logger.info("Received stop signal, shutting down...")
    shutdown_event.set()

async def main():
    token = get_env("TOKEN")
    bot   = Bot(command_path="peerless/commands")

    # Register signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    logger.info("Starting bot...")
    async with bot:
        setup_discord_logger(bot)

        bot.cache = Cache(bot=bot)
        bot.database = Database(cache=bot.cache)

        await bot.cache.connect()
        bot.cache.load_endpoints('peerless/ipc')
        await bot.database.connect()

        bot_task = asyncio.create_task(bot.start(token))
        shutdown_task = asyncio.create_task(shutdown_event.wait())

        done, pending = await asyncio.wait(
            [bot_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        if shutdown_task in done:
            logger.info("Shutdown event triggered. Stopping bot.")
            await bot.close()

        for task in pending:
            task.cancel()

    await bot.cache.close()
    await bot.database.close()
    await bot.close()
    await bot.http.close()

    logger.info("Bot has shut down.")

if __name__ == "__main__":
    asyncio.run(main())