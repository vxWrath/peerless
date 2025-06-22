import datetime
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Self,
    Set,
    Tuple,
    Type,
    Union,
    overload,
)
from uuid import uuid4

import discord
from discord.utils import MISSING
from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ConfigDict,
    Field,
    ModelWrapValidatorHandler,
    PrivateAttr,
    model_validator,
)

from .exceptions import TeamWithoutRole
from .namespace import Namespace
from .settings import SETTINGS, SettingType

if TYPE_CHECKING:
    from .database import Database

__all__ = (
    'LeagueData',
    'SettingData',
    'TeamData',
    'RolePing',
    'GlobalPing',
    'PlayerData',
    'PlayerLeagueData',
    'DemandData',
    'SuspensionData',
    'ContractData',
)

class DataModel(PydanticBaseModel, Mapping):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    _db: 'Database' = PrivateAttr(init=False)

    @model_validator(mode='wrap')
    @classmethod
    def model_validator(cls: Type[Self], data: Dict[str, Any], handler: ModelWrapValidatorHandler[Self]) -> Self:
        for key, field in cls.model_fields.items():
            if (val := data.get(key, MISSING)) is MISSING:
                continue

            if field.annotation and isinstance(val, dict) and Namespace in field.annotation.mro():
                data[key] = Namespace(val)

        return handler(data)

    def __getattribute__(self, key: str) -> Any:
        if (
            key in super().__getattribute__('__pydantic_fields__').keys()
            and key not in super().__getattribute__('__pydantic_fields_set__')
        ):
            raise ValueError(f"'{self.__class__.__name__}.{key}' is not currently available. Make sure it has been retrieved.")
        
        return super().__getattribute__(key)
    
    def __setitem__(self, key: str, val: Any) -> None:
        setattr(self, key, val)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)
    
    def __len__(self) -> int:
        return len(self.model_dump())
    
    def __repr_args__(self):
        computed_fields_repr_args = [
            (k, getattr(self, k)) for k, v in self.__pydantic_computed_fields__.items() if v.repr
        ]

        for k, v in self.__dict__.items():
            if k not in self.__pydantic_fields_set__:
                continue

            field = self.__pydantic_fields__.get(k)
            if field and field.repr:
                if v is not self:
                    yield k, v
                else:
                    yield k, self.__repr_recursion__(v)

        try:
            pydantic_extra = object.__getattribute__(self, '__pydantic_extra__')
        except AttributeError:
            pydantic_extra = None

        if pydantic_extra is not None:
            yield from ((k, v) for k, v in pydantic_extra.items())
        yield from computed_fields_repr_args
    
    def bind(self, db: 'Database') -> Self:
        self._db = db
        return self

class LeagueData(DataModel):
    id: int
    teams: Namespace[str, 'TeamData'] = Field(default_factory=Namespace)
    settings: Namespace[str, 'SettingData[Any]'] = Field(default_factory=Namespace)

    async def update(self, keys: Set[str]) -> Self:
        if self._db is None:
            raise ValueError("Database not bound to this LeagueData instance.")
        
        await self._db.update_league(self, keys=keys)
        return self

    @cached_property
    def guild(self) -> discord.Guild:
        if self._db is None or not hasattr(self._db.cache, 'bot') or self._db.cache.bot is None:
            raise ValueError("Database not bound to this LeagueData instance.")
        
        guild = self._db.cache.bot.get_guild(self.id)

        if guild is None:
            # Purposefully not using fetch_guild here, because:
            # 1. This would have to be awaited
            # 2. It should be cached because you should only retrieve league data for guilds that are in this shard
            #    Possible edge case: Bot cache not ready, but commands are being executed
            raise ValueError(f"Guild with ID {self.id} not found in the bot's cache.")
        
        return guild

    # TODO: Add an overload for 'operations'
    # ^ also need to actually implement the operations setting type
    @overload
    def get_setting(self, name: str, /, *, type: Literal['alert', 'status']) -> 'SettingData[bool]': ...

    @overload
    def get_setting(self, name: str, /, *, type: Literal['channel', 'day', 'number']) -> 'SettingData[int]': ...

    @overload
    def get_setting(self, name: str, /, *, type: Literal['role']) -> 'SettingData[List[int]]': ...

    @overload
    def get_setting(self, name: str, /, *, type: Literal['ping']) -> 'SettingData[Union[RolePing, GlobalPing]]': ...

    def get_setting(self, name: str, /, *, type: SettingType) -> 'SettingData[Any]': # type parameter is strictly for type checking
        """Retrieve a setting by its name and type. If the setting is not found, it raises a KeyError."""
        val = self.settings.get(name)

        if val is None:
            raise KeyError(f"Setting '{name}' not set in league ID '{self.id}' settings.")

        setting = SETTINGS[name]
        return SettingData(value=setting.default_value, type=setting.type)

    async def get_team(self, *, token: Optional[str]=None, role_id: Optional[int]=None, emoji_id: Optional[int]=None) -> Tuple[Optional['TeamData'], Optional[discord.Role], Optional[discord.Emoji]]:
        """Retrieve a team based on the provided parameters. It can search by token, role_id, or emoji_id because they are all unique identifiers for a team."""
        if not token and not role_id and not emoji_id:
            raise ValueError("At least one of 'token', 'role_id', or 'emoji_id' must be provided.")

        possible_team: Optional['TeamData'] = None

        if token:
            possible_team = next((x for x in self.teams.values() if x.token == token), None)

        if role_id and not possible_team:
            possible_team = next((x for x in self.teams.values() if x.role_id == role_id), None)

        if emoji_id and not possible_team:
            possible_team = next((x for x in self.teams.values() if x.emoji_id == emoji_id), None)

        if not possible_team:
            return (None, None, None)
        
        role  = None
        emoji = None

        if possible_team.role_id:
            role = self.guild.get_role(possible_team.role_id)

            if not role:
                role = await self.guild.fetch_role(possible_team.role_id)

            if not role:
                await self.remove_from_team(possible_team, 'role_id')
            
        if possible_team.emoji_id:
            emoji = self.guild.get_emoji(possible_team.emoji_id)

            if not emoji:
                emoji = await self.guild.fetch_emoji(possible_team.emoji_id)

            if not emoji:
                await self.remove_from_team(possible_team, 'emoji_id')

        if not role:
            raise TeamWithoutRole(possible_team)

        return (possible_team, role, emoji)

    async def remove_from_team(self, team: 'TeamData', field: Literal['emoji_id', 'role_id']) -> None:
        """Remove a field from a team. This is used to remove the emoji or role from a team if it no longer exists."""
        if self._db is None:
            raise ValueError("Database not bound to this LeagueData instance.")
        
        if not getattr(team, field, None):
            return
        
        setattr(team, field, None)
        await self.update({'teams'})

    def get_player_team(self, member: discord.Member) -> Optional['TeamData']:
        """Get the team of a player based on their member object. It is recommended to use 'get_team' immediately after this to get the role and emoji."""
        
        # Possible change return type to Optional[Tuple['TeamData', discord.Role, discord.Emoji]] if you want to return the role and emoji as well
        # Stops you from having to call get_team after this
        for team in self.teams.values():
            if team.role_id and team.role_id in member._roles: # Kinda hacky, but _roles is a hashmap
                return team
            
        return None

class SettingData[V: Any](PydanticBaseModel):
    value: V
    type: SettingType

class RolePing(PydanticBaseModel):
    key: Literal["role"]
    value: List[int]

class GlobalPing(PydanticBaseModel):
    key: Literal["everyone", "here"]
    value: None

class TeamData(PydanticBaseModel):
    token: str = Field(default_factory=lambda : str(uuid4()))

    role_name: str
    role_id: Optional[int] = None
    emoji_id: Optional[int] = None

class CoachData(PydanticBaseModel):
    token: str = Field(default_factory=lambda : str(uuid4()))

    role_id: Optional[int] = None
    acronym: Optional[str] = None

    # TODO: implement something like 'TeamData' for this class
    # need to update schema.py to reflect this change

class PlayerData(DataModel):
    id: int
    leagues: Namespace[int, 'PlayerLeagueData'] = Field(default_factory=Namespace)

    def __getattribute__(self, key: str) -> Any:
        return super(PydanticBaseModel, self).__getattribute__(key)

class PlayerLeagueData(DataModel):
    player_id: int
    league_id: int

    demands: 'DemandData' = Field(default_factory=lambda: DemandData(remaining=3, available_at=datetime.datetime.now()))
    suspension: Optional['SuspensionData'] = None
    contract: Optional['ContractData'] = None

    appointed_at: Optional[datetime.datetime] = None
    waitlisted_at: Optional[datetime.datetime] = None
    blacklisted: bool = False

    @property
    def id(self) -> Tuple[int, int]:
        return (self.player_id, self.league_id)

class DemandData(PydanticBaseModel):
    remaining: int
    available_at: datetime.datetime

class SuspensionData(PydanticBaseModel):
    reason: Optional[str]
    until: datetime.datetime
    banned: bool
    proof: Optional[List[str]]

class ContractData(PydanticBaseModel):
    team_token: str
    notes: str
    salary: Optional[float]
    length: float