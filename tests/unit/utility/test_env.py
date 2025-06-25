import pytest
import os
from unittest.mock import patch
from utility.env import get_env

class TestEnv:
    def test_get_env_existing_variable(self):
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = get_env("TEST_VAR")
            assert result == "test_value"

    def test_get_env_with_default(self):
        result = get_env("NONEXISTENT_VAR", "default_value")
        assert result == "default_value"

    def test_get_env_missing_no_default(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit):
                get_env("NONEXISTENT_VAR")
