import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Self,
    Tuple,
    Type,
    TypedDict,
)
from uuid import uuid4

from discord.utils import MISSING
from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ConfigDict,
    Field,
    ModelWrapValidatorHandler,
    PrivateAttr,
    model_validator,
)

from .namespace import Namespace

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
)

type SettingType = Literal['alert', 'channel', 'day', 'number', 'option', 'ping', 'role', 'status', 'theme', 'timezone']

class DataModel(PydanticBaseModel, Mapping):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    @model_validator(mode='wrap')
    @classmethod
    def model_validator(cls: Type[Self], data: Dict[str, Any], handler: ModelWrapValidatorHandler) -> Self:
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
    
class LeagueData(DataModel):
    id: int
    teams: Namespace[str, 'TeamData'] = Field(default_factory=Namespace)
    settings: Namespace[str, 'SettingData[Any]'] = Field(default_factory=Namespace)

    _db: 'Database' = PrivateAttr(init=False)

class SettingData[V: Any](PydanticBaseModel):
    value: V
    type: SettingType

class RolePing(TypedDict):
    key: Literal["role"]
    value: List[int]

class GlobalPing(TypedDict):
    key: Literal["everyone", "here"]
    value: None

class TeamData(PydanticBaseModel):
    token: str = Field(default_factory=lambda : str(uuid4()))

    role_name: str
    role_id: Optional[int] = None
    emoji_id: Optional[int] = None

class PlayerData(DataModel):
    id: int
    leagues: Namespace[int, 'PlayerLeagueData'] = Field(default_factory=Namespace)

    _db: 'Database' = PrivateAttr(init=False)

    def __getattribute__(self, key: str) -> Any:
        return super(PydanticBaseModel, self).__getattribute__(key)

class PlayerLeagueData(DataModel):
    player_id: int
    league_id: int

    demands: 'DemandData' = Field(default_factory=lambda: DemandData(remaining=0, available_at=datetime.datetime.now()))
    suspension: Optional['SuspensionData'] = None
    contract: Optional['ContractData'] = None

    appointed_at: Optional[datetime.datetime] = None
    waitlisted_at: Optional[datetime.datetime] = None
    blacklisted: bool = False

    _db: 'Database' = PrivateAttr(init=False)

    @property
    def id(self) -> Tuple[int, int]:
        return (self.player_id, self.league_id)

class DemandData(TypedDict):
    remaining: int
    available_at: datetime.datetime

class SuspensionData(TypedDict):
    reason: Optional[str]
    until: datetime.datetime
    banned: bool
    proof: Optional[List[str]]

class ContractData(TypedDict):
    team_token: str
    notes: str
    salary: Optional[float]
    length: float