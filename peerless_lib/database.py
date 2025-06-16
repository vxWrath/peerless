import json
import os
from enum import Enum
from typing import Any, Optional, Set, Union

import asyncpg

from .models import LeagueData, PlayerData, PlayerLeagueData

__all__ = (
    'Database',
)

class Table(str, Enum):
    PLAYERS = "players"
    LEAGUES = "leagues"
    PLAYER_LEAGUES = "player_leagues"

def _dumps(obj: Any):
    return json.dumps(obj)

def _loads(obj: Any):
    if obj == '"{}"':
        return dict()
    return json.loads(obj)

async def postgres_initializer(con):
    await con.set_type_codec(
        'jsonb',
        encoder=_dumps,
        decoder=_loads,
        schema='pg_catalog',
        format='text'
    )

class Database:
    def __init__(self) -> None:
        self.pool: asyncpg.Pool

    async def connect(self) -> None:
        """Connect to the PostgreSQL database."""
        self.pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL", ""), init=postgres_initializer)

    async def close(self) -> None:
        """Close the database connection pool."""
        if hasattr(self, 'pool'):
            await self.pool.close()

    async def insert(self, table: Table, model: Union[LeagueData, PlayerData, PlayerLeagueData], excluded: Set[str]) -> None:
        dump = model.model_dump(mode='json', exclude=excluded)

        try:
            await self.pool.execute(f"""
                INSERT INTO {table.value} ({', '.join(dump.keys())}) 
                VALUES ({', '.join(f'${i}' for i in range(1, len(dump.values())+1))});
            """, *dump.values())
        except asyncpg.UniqueViolationError:
            raise ValueError(f"{model.__class__.__name__} with ID {model.id} already exists.")
        except asyncpg.PostgresError as e:
            raise RuntimeError(f"Database error during insert: {e}")

    async def update(self, table: Table, model: Union[LeagueData, PlayerData, PlayerLeagueData], *, keys: Set[str]) -> None:
        dump = model.model_dump(mode='json', include=set(keys))

        try:
            if isinstance(model, PlayerLeagueData):
                await self.pool.execute(f"""
                    UPDATE {table.value} 
                    SET {', '.join(f"{key}=${i}" for i, key in enumerate(dump.keys(), 1))} 
                    WHERE player_id={len(dump.keys())+1} AND league_id={len(dump.keys())+2};
                """, *dump.values(), model.player_id, model.league_id)
            else:
                await self.pool.execute(f"""
                    UPDATE {table.value} 
                    SET {', '.join(f"{key}=${i}" for i, key in enumerate(dump.keys(), 1))} 
                    WHERE id={len(dump.keys())+1};
                """, *dump.values(), model.id)
        except asyncpg.PostgresError as e:
            raise RuntimeError(f"{model.__class__.__name__} with ID {model.id} had trouble being updated: {e}")

    async def delete(self, table: Table, model: Union[LeagueData, PlayerData, PlayerLeagueData]) -> None:
        try:
            if isinstance(model, PlayerLeagueData):
                await self.pool.execute(f"""
                    DELETE FROM {table.value} WHERE player_id=$1 AND league_id=$2
                """, model.player_id, model.league_id)
            else:
                await self.pool.execute(f"""
                    DELETE FROM {table.value} WHERE id=$1
                """, model.id)
        except asyncpg.PostgresError as e:
            raise RuntimeError(f"{model.__class__.__name__} with ID {model.id} could not be deleted: {e}")

    async def create_league(self, league_id: int, *, keys: Set[str]) -> LeagueData:
        league_data = LeagueData(id=league_id)
        league_data.__pydantic_fields_set__.update(keys)
        league_data._db = self

        await self.insert(
            table = Table.LEAGUES,
            model = league_data,
            excluded = set()
        )

        return league_data
    
    async def create_player(self, player_id: int) -> PlayerData:
        player_data = PlayerData(id=player_id)
        player_data.__pydantic_fields_set__.update({"leagues"})
        player_data._db = self

        await self.insert(
            table = Table.PLAYERS,
            model = player_data,
            excluded = {'leagues'}
        )

        return player_data
    
    async def create_player_league(self, player_data: PlayerData, league_data: LeagueData) -> PlayerLeagueData:
        player_league_data = PlayerLeagueData(player_id=player_data.id, league_id=league_data.id)
        player_league_data.__pydantic_fields_set__.update(PlayerLeagueData.model_fields.keys())
        player_league_data._db = self

        await self.insert(
            table = Table.PLAYER_LEAGUES,
            model = player_league_data,
            excluded = set()
        )

        return player_league_data
    
    async def update_league(self, league_data: LeagueData, *, keys: Set[str]) -> None:
        await self.update(Table.LEAGUES, league_data, keys=keys)

    async def update_player_league(self, player_league_data: PlayerLeagueData, *, keys: Set[str]):
        await self.update(Table.PLAYER_LEAGUES, player_league_data, keys=keys)

    async def fetch_league(self, league_id: int, *, keys: Set[str]) -> Optional[LeagueData]:
        necessary_keys = {'id'}
        necessary_keys.update(keys)

        data = await self.pool.fetchrow(f"SELECT {', '.join(necessary_keys)} FROM {Table.LEAGUES.value} WHERE id=$1", league_id)

        if not data:
            return None
        
        league_data = LeagueData.model_validate(dict(data))
        league_data._db = self

        return league_data
    
    async def fetch_player(self, player_id: int, league_id: int, *, keys: Set[str]) -> Optional[PlayerData]:
        necessary_keys = {'player_id', 'league_id'}
        necessary_keys.update(keys)

        data = await self.pool.fetchrow(f"SELECT id FROM {Table.PLAYERS.value} WHERE id=$1", player_id)

        if not data:
            return None
        
        player_data = PlayerData.model_validate(dict(data) | {"leagues": {}})
        player_data._db = self

        data = await self.pool.fetchrow(f"SELECT {', '.join(necessary_keys)} FROM {Table.PLAYER_LEAGUES.value} WHERE player_id=$1 AND league_id=$2", player_id, league_id)
        if data:
            player_league_data = PlayerLeagueData.model_validate(dict(data))
            player_league_data._db = self

            player_data.leagues[player_league_data.league_id] = player_league_data

        return player_data
    
    async def produce_league(self, league_id: int, *, keys: Set[str]) -> LeagueData:
        league_data = await self.fetch_league(league_id, keys=keys)

        if not league_data:
            league_data = await self.create_league(league_id, keys=keys)

        return league_data
    
    async def produce_player(self, player_id: int, league_data: Optional[LeagueData]=None, *, keys: Optional[Set[str]]=None) -> PlayerData:
        player_data = await self.fetch_player(player_id, league_data.id if league_data else 0, keys=keys or set())

        if not player_data:
            player_data = await self.create_player(player_id)

        if league_data and not player_data.leagues.get(league_data.id):
            player_league_data = await self.create_player_league(player_data, league_data)
            player_data.leagues[player_league_data.league_id] = player_league_data

        return player_data