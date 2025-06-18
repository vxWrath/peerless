import json
from typing import Any, Optional, Set, Union

import asyncpg
from discord.utils import MISSING
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .cache import Cache
from .env import get_env
from .logger import get_logger
from .models import LeagueData, PlayerData, PlayerLeagueData
from .query_builder import Query
from .schema import Table, create_missing_tables

__all__ = (
    'Database',
)

log = get_logger()

def _dumps(obj: Any):
    return json.dumps(obj)

def _loads(obj: Any):
    if obj == '"{}"':
        return dict()
    return json.loads(obj)

async def postgres_initializer(con):
    """Set up custom JSONB codec for asyncpg connections."""

    await con.set_type_codec(
        'jsonb',
        encoder=_dumps,
        decoder=_loads,
        schema='pg_catalog',
        format='text'
    )

class Database:
    """Database class for handling PostgreSQL and cache operations."""

    def __init__(self, cache: Cache) -> None:
        self.cache = cache
        self.pool: asyncpg.Pool

    async def connect(self) -> None:
        """Connect to the PostgreSQL database and ensure required tables exist."""

        await self._handle_connect()

        # Ensure Redis cache is connected
        if not self.cache.redis.connection or not self.cache.redis.connection.is_connected:
            await self.cache.connect()

        # Check for missing tables and create them if necessary
        table_names = [table.value for table in Table]
        existing_tables = await self.pool.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        existing_table_names = {row['table_name'] for row in existing_tables}
        missing_tables = [table for table in table_names if table not in existing_table_names]

        if missing_tables:
            # Blocking but quick operation to create missing tables
            create_missing_tables(missing_tables)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((asyncpg.PostgresError,))
    )
    async def _handle_connect(self) -> None:
        """Create asyncpg connection pool with retry logic."""

        self.pool = await asyncpg.create_pool(dsn=get_env("DATABASE_URL"), init=postgres_initializer)
        log.info("Connected to PostgreSQL")

    async def close(self) -> None:
        """Close the database connection pool."""

        if hasattr(self, 'pool'):
            await self.pool.close()

        log.info("Closed PostgreSQL connection")

    async def insert(self, table: Table, model: Union[LeagueData, PlayerData, PlayerLeagueData], excluded: Set[str]) -> None:
        """Insert a model into a database table."""

        dump = model.model_dump(mode='json', exclude=excluded)
        query, args = Query.insert(table=table.value, values=dump)

        try:
            await self.pool.execute(query, *args)
            log.debug(f"Inserted ID {model.id} into table {table.value!r}")
        except asyncpg.UniqueViolationError:
            log.error(f"{model.__class__.__name__} with ID {model.id} already exists in table {table.value!r}")
        except asyncpg.PostgresError as e:
            log.error(f"Database error while trying to insert into table {table.value!r} with ID {model.id}", exc_info=e)

    async def update(self, table: Table, model: Union[LeagueData, PlayerData, PlayerLeagueData], *, keys: Set[str]) -> None:
        """Update data in a database table."""

        dump = model.model_dump(mode='json', include=set(keys))

        if isinstance(model, PlayerLeagueData):
            where = {"player_id": model.player_id, "league_id": model.league_id}
        else:
            where = {"id": model.id}

        query, args = Query.update(table=table.value, values=dump, where=where)

        try:
            await self.pool.execute(query, *args)
            log.debug(f"Updated ID {model.id} with keys {keys} in table {table.value!r}")
        except asyncpg.PostgresError as e:
            log.error(f"Database error while trying to update table {table.value!r} with ID {model.id}", exc_info=e)

    async def delete(self, table: Table, model: Union[LeagueData, PlayerData, PlayerLeagueData]) -> None:
        """Delete data from a database table."""

        if isinstance(model, PlayerLeagueData):
            where = {"player_id": model.player_id, "league_id": model.league_id}
        else:
            where = {"id": model.id}

        query, args = Query.delete(table=table.value, where=where)

        try:
            await self.pool.execute(query, *args)
            log.debug(f"Deleted ID {model.id} from table {table.value!r}")
        except asyncpg.PostgresError as e:
            log.error(f"Database error while trying to delete table {table.value!r} with ID {model.id}", exc_info=e)

    async def create_league(self, league_id: int, *, keys: Set[str]) -> LeagueData:
        """Create a new LeagueData entry in the database."""

        league_data = LeagueData(id=league_id).bind(self)
        league_data.__pydantic_fields_set__.update(keys)

        await self.insert(
            table = Table.LEAGUES,
            model = league_data,
            excluded = set()
        )

        return league_data
    
    async def create_player(self, player_id: int) -> PlayerData:
        """Create a new PlayerData entry in the database."""

        player_data = PlayerData(id=player_id).bind(self)
        player_data.__pydantic_fields_set__.update({"leagues"})

        await self.insert(
            table = Table.PLAYERS,
            model = player_data,
            excluded = {'leagues'}
        )

        return player_data

    async def create_player_league(self, player_data: PlayerData, league_data: LeagueData, *, keys: Set[str]) -> PlayerLeagueData:
        """Create a new PlayerLeagueData entry in the database."""

        player_league_data = PlayerLeagueData(player_id=player_data.id, league_id=league_data.id).bind(self)
        player_league_data.__pydantic_fields_set__.update(keys)

        await self.insert(
            table = Table.PLAYER_LEAGUES,
            model = player_league_data,
            excluded = set()
        )

        return player_league_data
    
    async def update_league(self, league_data: LeagueData, *, keys: Set[str]) -> None:
        """Update LeagueData in the database and cache."""

        await self.update(Table.LEAGUES, league_data, keys=keys)
        await self.cache.hash_set(league_data, identifier=str(league_data.id), keys=keys)

    async def update_player_league(self, player_league_data: PlayerLeagueData, *, keys: Set[str]) -> None:
        """Update PlayerLeagueData in the database and cache."""

        await self.update(Table.PLAYER_LEAGUES, player_league_data, keys=keys)
        await self.cache.hash_set(player_league_data, identifier=f"{player_league_data.player_id}:{player_league_data.league_id}", keys=keys)

    async def fetch_league(self, league_id: int, *, keys: Set[str]) -> Optional[LeagueData]:
        """Fetch LeagueData from the cache with fallback to the database."""

        necessary_keys = {'id'}
        necessary_keys.update(keys)

        league_data, missing = await self.cache.hash_get(LeagueData, identifier=str(league_id), keys=keys)

        try:
            if league_data and missing:
                # Fetch missing fields from database
                query, args = Query.select(table=Table.LEAGUES.value, columns=missing, where={"id": league_id})
                data = await self.pool.fetchrow(query, *args)

                if not data:
                    log.debug(f"No data found for ID '{league_id}' in {Table.LEAGUES.value!r} database")
                    return None
                
                league_data = league_data.model_validate(dict(data) | league_data.model_dump(include=necessary_keys))
                log.debug(f"Fetched missing keys for ID '{league_id}' from {Table.LEAGUES.value!r} database")
                await self.cache.hash_set(league_data, identifier=str(league_id), keys=necessary_keys)

            elif not league_data:
                # Fetch all necessary fields from database
                query, args = Query.select(table=Table.LEAGUES.value, columns=necessary_keys, where={"id": league_id})
                data = await self.pool.fetchrow(query, *args)

                if not data:
                    log.debug(f"No data found for ID '{league_id}' in {Table.LEAGUES.value!r} database")
                    return None
                
                league_data = LeagueData.model_validate(dict(data))
                log.debug(f"Fetched data for ID '{league_id}' from {Table.LEAGUES.value!r} database")
                await self.cache.hash_set(league_data, identifier=str(league_id), keys=missing or set())
        except asyncpg.PostgresError as e:
            log.error(f"Database error while trying to select from table {Table.LEAGUES.value!r} with ID {league_id}")
            raise e
        
        return league_data.bind(self)

    async def fetch_player(self, player_id: int, league_id: Optional[int], *, keys: Set[str]) -> Optional[PlayerData]:
        """Fetch PlayerData (and optionally PlayerLeagueData) from the cache with fallback to the database."""

        necessary_keys = {'player_id', 'league_id'}
        necessary_keys.update(keys)

        player_data, _ = await self.cache.hash_get(PlayerData, identifier=str(player_id), keys={'id'})

        if not league_id:
            player_league_data = None
            missing = MISSING
        else:
            player_league_data, missing = await self.cache.hash_get(PlayerLeagueData, identifier=f"{player_id}:{league_id}", keys=necessary_keys)

        if not player_data or missing:
            try:
                if not player_data:
                    # Fetch PlayerData from database
                    data = await self.pool.fetchrow(f"SELECT id FROM {Table.PLAYERS.value} WHERE id=$1", player_id)

                    if not data:
                        log.debug(f"No data found for ID {player_id} in {Table.PLAYERS.value!r} database")
                        return None
                    
                    player_data = PlayerData.model_validate(dict(data) | {"leagues": {}})
                    log.debug(f"Fetched data for ID '{player_id}' from {Table.PLAYERS.value!r} database")
                    await self.cache.hash_set(player_data, identifier=str(player_id), keys={'id'})

                if missing != MISSING and not player_league_data:
                    # Fetch PlayerLeagueData from database
                    data = await self.pool.fetchrow(f"SELECT {', '.join(necessary_keys)} FROM {Table.PLAYER_LEAGUES.value} WHERE player_id=$1 AND league_id=$2", player_id, league_id)

                    if data:
                        player_league_data = PlayerLeagueData.model_validate(dict(data))
                        log.debug(f"Fetched data for ID '{player_id}:{league_id}' from {Table.PLAYER_LEAGUES.value!r} database")
                        await self.cache.hash_set(player_league_data, identifier=f"{player_id}:{league_id}", keys=necessary_keys)

                # If some keys are missing, fetch them
                elif missing != MISSING and player_league_data and missing:
                    data = await self.pool.fetchrow(f"SELECT {', '.join(missing)} FROM {Table.PLAYER_LEAGUES.value} WHERE player_id=$1 AND league_id=$2", player_id, league_id)

                    if data:
                        player_league_data = player_league_data.model_validate(dict(data) | player_league_data.model_dump(include=necessary_keys))

                        log.debug(f"Fetched missing keys for ID '{player_id}:{league_id}' from {Table.PLAYER_LEAGUES.value!r} database")
                        await self.cache.hash_set(player_league_data, identifier=f"{player_id}:{league_id}", keys=missing)
                    else:
                        # No data found for missing keys (Should not happen)
                        player_league_data = None

            except asyncpg.PostgresError as e:
                log.error(f"Database error while trying to select player data with ID {player_id}:{league_id}")
                raise e     

        player_data.__pydantic_fields_set__.update({"leagues"})

        if player_league_data:
            player_league_data.bind(self)
            player_data.leagues[player_league_data.league_id] = player_league_data

        return player_data.bind(self)
    
    async def produce_league(self, league_id: int, *, keys: Set[str]) -> LeagueData:
        """Fetch or create a LeagueData entry."""

        league_data = await self.fetch_league(league_id, keys=keys)

        if not league_data:
            league_data = await self.create_league(league_id, keys=keys)

        return league_data
    
    async def produce_player(self, player_id: int, league_data: Optional[LeagueData]=None, *, keys: Optional[Set[str]]=None) -> PlayerData:
        """Fetch or create a PlayerData entry, and optionally PlayerLeagueData."""

        player_data = await self.fetch_player(player_id, league_data.id if league_data else None, keys=keys or set())

        if not player_data:
            player_data = await self.create_player(player_id)

        if league_data and not player_data.leagues.get(league_data.id):
            player_league_data = await self.create_player_league(player_data, league_data, keys=keys or set())
            player_data.leagues[player_league_data.league_id] = player_league_data
            
        return player_data