from __future__ import annotations

from typing import TYPE_CHECKING, List

import discord

if TYPE_CHECKING:
    from .checks import Check
    from .models import TeamData

__all__ = (
    'PeerlessException',
    'PeerlessDown',
    'CheckFailure',
    'RolesNotAssignable',
    'RolesAlreadyManaged',
    'RolesAlreadyUsed',
    'NotEnoughTeams',
    'TeamWithoutRole',
)

class PeerlessException(Exception):
    """Base exception for all peerless errors"""
    pass

class PeerlessDown(Exception):
    pass

class CheckFailure(discord.app_commands.CheckFailure):
    def __init__(self, check: 'Check'):
        self.check = check

class RolesNotAssignable(PeerlessException):
    def __init__(self, roles: List[discord.Role]):
        self.roles = roles
        
class RolesAlreadyManaged(PeerlessException):
    def __init__(self, roles: List[discord.Role]):
        self.roles = roles
        
class RolesAlreadyUsed(PeerlessException):
    def __init__(self, roles: List[discord.Role]):
        self.roles = roles

class NotEnoughTeams(PeerlessException):
    def __init__(self, required: int):
        self.required = required

class TeamWithoutRole(PeerlessException):
    def __init__(self, team: TeamData):
        self.team = team