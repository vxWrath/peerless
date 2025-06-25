from typing import Any, Dict, Optional

from discord import Permissions
from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ConfigDict,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

__all__ = (
    'DiscordUser',
    'DiscordPartialGuild',
)

class DiscordUser(PydanticBaseModel):
    session_token: str
    
    id: int
    username: str
    avatar: Optional[str]
    global_name: str

    @computed_field
    def avatar_url(self) -> str:
        if not self.avatar:
            return 'https://cdn.discordapp.com/embed/avatars/1.png'
        
        animated = self.avatar.startswith('a_')
        image_format = 'gif' if animated else 'png'

        return f'https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.{image_format}?size=1024'
    
class DiscordPartialGuild(PydanticBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    name: str
    icon: Optional[str]
    banner: Optional[str]
    owner: bool
    permissions: Permissions

    @field_validator('permissions', mode='wrap')
    @classmethod
    def perm_validator(cls, value: str | int, handler: ...) -> Permissions:
        if isinstance(value, int):
            v = Permissions._from_value(value)
        elif value.isdigit():
            v = Permissions._from_value(int(value))
        else:
            raise ValueError(f'Invalid permissions value: {value}')
        
        return handler(v)
    
    @field_serializer('permissions')
    def perm_serializer(self, permissions: Permissions) -> int:
        return permissions.value
    
    @model_validator(mode='before')
    @classmethod
    def model_validate(cls, data: Dict[str, Any]) -> Any:  
        data['permissions'] = data.pop('permissions_new', None) or data['permissions']
        return data
    
    @computed_field
    def icon_url(self) -> str:
        if not self.icon:
            return 'https://cdn.discordapp.com/embed/avatars/1.png'
        
        animated = self.icon.startswith('a_')
        image_format = 'gif' if animated else 'png'
        
        return f'https://cdn.discordapp.com/icons/{self.id}/{self.icon}.{image_format}?size=1024'