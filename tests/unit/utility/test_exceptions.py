import pytest
import discord
from unittest.mock import MagicMock
from utility.exceptions import (
    PeerlessException,
    CheckFailure,
    RolesNotAssignable,
    RolesAlreadyManaged,
    NotEnoughTeams
)
from utility.checks import Check

class TestExceptions:
    def test_peerless_exception(self):
        exc = PeerlessException("Test message")
        assert str(exc) == "Test message"

    def test_check_failure(self):
        check = Check.DEVELOPER
        exc = CheckFailure(check)
        assert exc.check == check

    def test_roles_not_assignable(self):
        mock_role = MagicMock(spec=discord.Role)
        mock_role.name = "TestRole"
        roles = [mock_role]
        exc = RolesNotAssignable(roles)
        assert exc.roles == roles

    def test_roles_already_managed(self):
        mock_role = MagicMock(spec=discord.Role)
        roles = [mock_role]
        exc = RolesAlreadyManaged(roles)
        assert exc.roles == roles

    def test_not_enough_teams(self):
        required = 5
        exc = NotEnoughTeams(required)
        assert exc.required == required
