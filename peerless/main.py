import asyncio
import signal

from utility import (
    Bot,
    Cache,
    Database,
    create_logged_task,
    get_env,
    get_logger,
    setup_discord_logger,
)

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

        bot.cache = Cache(endpoints_folder='peerless/ipc', bot=bot)
        bot.database = Database(cache=bot.cache)

        await bot.cache.connect()
        await bot.database.connect()

        bot_task = create_logged_task(bot.start(token), name="bot_start")
        shutdown_task = create_logged_task(shutdown_event.wait(), name="shutdown_event")

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
    bot.clear()

    logger.info("Bot has shut down.")

if __name__ == "__main__":
    asyncio.run(main())