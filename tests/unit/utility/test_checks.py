import pytest
from unittest.mock import MagicMock
import discord
from utility.checks import is_developer, DEV_IDS

class TestChecks:
    def test_is_developer_true(self):
        mock_user = MagicMock(spec=discord.User)
        mock_user.id = DEV_IDS[0]
        assert is_developer(mock_user) is True

    def test_is_developer_false(self):
        mock_user = MagicMock(spec=discord.User)
        mock_user.id = 999999999
        assert is_developer(mock_user) is False

    def test_is_developer_with_member(self):
        mock_member = MagicMock(spec=discord.Member)
        mock_member.id = DEV_IDS[0]
        assert is_developer(mock_member) is True
