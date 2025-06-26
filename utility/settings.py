
import json
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel

from .namespace import Namespace

__all__ = (
    'SETTINGS',
    'Setting',
    'SettingSupportsOptions',
    'SettingSupportsMinMax',
    'Option',
)

type SettingType = Literal['operations', 'alert', 'channel', 'day', 'number', 'option', 'ping', 'role', 'status', 'theme', 'timezone']

# These classes are subject to a lot of change
class Setting(BaseModel):
    name: str
    key: str
    default_value: Any
    type: SettingType
    description: str
    required: bool

class SettingSupportsOptions(Setting):
    options: List['Option']

class SettingSupportsMinMax(Setting):
    minimum: Optional[float]
    maximum: Optional[float]

class Option(BaseModel):
    name: str
    description: str

with open("utility/settings.json") as f:
    data: List[Dict[str, Any]] = json.load(f)

def _convert_to_setting(data: Dict[str, Any]) -> Union[Setting, SettingSupportsOptions, SettingSupportsMinMax]:
    if 'options' in data:
        return SettingSupportsOptions(**data)
    elif 'minimum' in data or 'maximum' in data:
        return SettingSupportsMinMax(**data)
    else:
        return Setting(**data)

SETTINGS: Namespace[str, Union[Setting, SettingSupportsOptions, SettingSupportsMinMax]] = Namespace(
    {item['name']: _convert_to_setting(item) for item in data}
)