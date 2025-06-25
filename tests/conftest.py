import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_redis():
    return AsyncMock()

@pytest.fixture
def mock_database():
    return AsyncMock()

@pytest.fixture
def mock_cache():
    cache = AsyncMock()
    cache.redis = AsyncMock()
    return cache
