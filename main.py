import asyncio

from utility import Cache, Database, get_logger

logger = get_logger()

async def main():
    cache = Cache()
    db = Database(cache)

    await cache.connect()
    await db.connect()

    league = await db.produce_league(league_id=1, keys={'settings'})
    player = await db.produce_player(player_id=1, league_data=league, keys={'appointed_at', 'suspension', 'contract'})

    logger.info(f"League data: {repr(league)}")
    logger.info(f"Player data: {repr(player)}")

    await cache.close()
    await db.close()

asyncio.run(main())