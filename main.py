import asyncio

from peerless_lib import Cache, Database, create_tables, get_logger

logger = get_logger()

FIRST_RUN = True # Set to False after you have ran the docker-compose command for the first time

async def main():
    if FIRST_RUN:
        create_tables()

    cache = Cache()
    db = Database(cache)

    await cache.connect()
    await db.connect()

    league = await db.produce_league(league_id=1, keys={'settings'})
    player = await db.produce_player(player_id=1, league_data=league)

    logger.info(f"League data: {league}")
    logger.info(f"Player data: {player}")

asyncio.run(main())