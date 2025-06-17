import asyncio

from peerless_lib import Cache, Database, get_logger

logger = get_logger()

async def main():
    cache = Cache()
    db = Database(cache)

    await cache.connect()
    await db.connect()

    league = await db.produce_league(league_id=1, keys={'settings'})
    player = await db.produce_player(player_id=1, league_data=league)

    logger.info(f"League data: {league}")
    logger.info(f"Player data: {player}")

asyncio.run(main())