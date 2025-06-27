from secrets import token_urlsafe
from typing import Any, Dict, Optional

from discord import Permissions
from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

__all__ = (
    'DiscordUser',
    'DiscordPartialGuild',
    'OAuthState'
)

class OAuthState(PydanticBaseModel):
    token: str = Field(default_factory=lambda: token_urlsafe(16))
    redirect_to: str

class DiscordUser(PydanticBaseModel):
    session_token: str = Field(default_factory=lambda: token_urlsafe(32))
    
    id: int
    username: str
    avatar: Optional[str]
    global_name: str
    guilds: Dict[int, 'DiscordPartialGuild'] = Field(default_factory=dict)

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
        try:
            v = Permissions._from_value(value if isinstance(value, int) else int(value))
        except Exception as e:
            raise ValueError(f'Invalid permissions value: {value}') from e
        
        return handler(v)
    
    @field_serializer('permissions')
    def perm_serializer(self, permissions: Permissions) -> int:
        return permissions.value
    
    @model_validator(mode='before')
    @classmethod
    def before_model_validate(cls, data: Dict[str, Any]) -> Any:  
        data['permissions'] = data.pop('permissions_new', None) or data['permissions']
        data['id'] = int(data['id'])
        return data
    
    @computed_field
    def icon_url(self) -> str:
        if not self.icon:
            return 'https://cdn.discordapp.com/embed/avatars/1.png'
        
        animated = self.icon.startswith('a_')
        image_format = 'gif' if animated else 'png'
        
        return f'https://cdn.discordapp.com/icons/{self.id}/{self.icon}.{image_format}?size=1024'