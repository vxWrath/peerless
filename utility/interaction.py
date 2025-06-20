from re import Pattern
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    List,
    Optional,
    Self,
    Set,
    Union,
)

import discord
from discord.ui.button import Button
from discord.ui.dynamic import BaseT, DynamicItem
from discord.ui.item import Item
from discord.ui.select import BaseSelect
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

if TYPE_CHECKING:
    from .bot import Bot

__all__ = (
    "DeferOptions",
    "DataOptions",
    "InteractionOptions",
    "BaseItem",
    "BaseView",
    "response",
    "item_check",
)

class DeferOptions(PydanticBaseModel):
    defer: bool = False
    ephemeral: bool = False
    thinking: bool = False

class DataOptions(PydanticBaseModel):
    retrieve: bool = False
    keys: Set[str] = Field(default_factory=set)

class InteractionOptions(PydanticBaseModel):
    defer_options: DeferOptions = Field(default_factory=DeferOptions)
    modal_response: bool = False

    league_data: DataOptions = Field(default_factory=DataOptions)
    player_data: DataOptions = Field(default_factory=DataOptions)

class BaseItem(DynamicItem[BaseT], template=''): # template is meant to be overridden in subclasses
    checks: List[Callable[[Any, discord.Interaction['Bot']], bool]] = []

    def __init__(self, item: BaseT, *, row: Optional[int] = None, options: Optional[InteractionOptions] = None) -> None:
        super().__init__(item=item, row=row)

        if not self._view or not isinstance(self._view, BaseView):
            self._view = BaseView(timeout=None)

        self.options = options or InteractionOptions()

    def __init_subclass__(cls, *, template: str | Pattern[str]) -> None:
        cls.checks = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)

            if callable(attr) and getattr(attr, "__is_check__", False):
                cls.checks.append(attr) # type: ignore
                
        return super().__init_subclass__(template=template)

    def require_guild(self, interaction: discord.Interaction['Bot']) -> discord.Guild:
        if interaction.guild is None:
            # Add a custom exception instead of a ValueError for better error handling
            raise ValueError("Interaction must be in a guild")

        return interaction.guild
    
    def require_user(self, interaction: discord.Interaction['Bot']) -> discord.User:
        if interaction.user is None or not isinstance(interaction.user, discord.User):
            # Add a custom exception instead of a ValueError for better error handling
            raise ValueError("interaction.user must be a User object")

        return interaction.user
    
    def require_member(self, interaction: discord.Interaction['Bot']) -> discord.Member:
        if interaction.user is None or not isinstance(interaction.user, discord.Member):
            # Add a custom exception instead of a ValueError for better error handling
            raise ValueError("interaction.user must be a Member object")

        return interaction.user

    async def interaction_check(self, interaction: discord.Interaction['Bot']) -> bool:
        interaction.extras['options'] = self.options

        if not await interaction.client.tree.interaction_check(interaction):
            return False
        
        if interaction.channel and interaction.channel.type == discord.ChannelType.private:
            return True
        
        for check in self.checks:
            if not await discord.utils.maybe_coroutine(check, self, interaction):
                return False

        return True

class BaseView(discord.ui.View):
    children: List[DynamicItem[Button[Self] | BaseSelect[Self]]] = []

    async def on_error(self, interaction: discord.Interaction['Bot'], error: Exception, _: Item[Any]) -> None:
        return await interaction.client.tree.on_error(interaction, error) # type: ignore

def item_check(func: Callable[[Any, discord.Interaction['Bot']], Union[bool, Awaitable[bool]]]):
    """Mark a method as a check for a BaseItem."""
    setattr(func, "__is_check__", True)
    return func

class response:
    @staticmethod
    async def send(interaction: discord.Interaction['Bot'], **kwargs) -> Union[discord.InteractionCallbackResponse['Bot'], discord.WebhookMessage]:
        if interaction.response.is_done():
            return await interaction.followup.send(**kwargs)
        else:
            return await interaction.response.send_message(**kwargs)
        
    @staticmethod
    async def edit(interaction: discord.Interaction['Bot'], **kwargs) -> Union[discord.InteractionCallbackResponse['Bot'], discord.InteractionMessage, None]:
        if interaction.response.is_done():
            return await interaction.edit_original_response(**kwargs)
        else:
            return await interaction.response.edit_message(**kwargs)