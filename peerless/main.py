import asyncio

from utility import Cache, Database, get_logger

logger = get_logger()

async def main():
    cache = Cache()
    db = Database(cache)

    await cache.connect()
    await db.connect()

    #league = await db.fetch_league(league_id=1, keys={'teams', 'settings'})
    #player = await db.fetch_player(player_id=1, league_id=1, keys={'demands', 'suspension', 'contract', 'appointed_at', 'waitlisted_at', 'blacklisted'})

    #logger.info(f"League data: {repr(league)}")
    #logger.info(f"Player data: {repr(player)}")

    await cache.close()
    await db.close()

asyncio.run(main())