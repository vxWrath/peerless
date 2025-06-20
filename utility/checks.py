from enum import Enum
from typing import TYPE_CHECKING, Literal

import discord

from .exceptions import CheckFailure

if TYPE_CHECKING:
    from .bot import Bot

__all__ = (
    'DEV_IDS',
    'is_developer',
    'developer_only',
    'guild_owner_only',
)

DEV_IDS = [
    1104883688279384156, # godmadewrath
    450136921327271946,  # wrath
    1030125659781079130, # veemills
    1010231134048759900, # lawless
    875219288502452254,  # kibs
    976237984766648370,  # sal
]

class Check(Enum):
    DEVELOPER = "developer_only"
    GUILD_OWNER = "guild_owner_only"

def is_developer(user: discord.User | discord.Member) -> bool:
    return user.id in DEV_IDS

def developer_only():
    async def pred(interaction: discord.Interaction['Bot']) -> Literal[True]:
        if is_developer(interaction.user):
            return True
        raise CheckFailure(Check.DEVELOPER)

    return discord.app_commands.check(pred)

def guild_owner_only():
    def pred(interaction: discord.Interaction['Bot']) -> Literal[True]:
        if interaction.guild and interaction.user.id != interaction.guild.owner_id:
            raise CheckFailure(Check.GUILD_OWNER)
        return True
        
    return discord.app_commands.check(pred)