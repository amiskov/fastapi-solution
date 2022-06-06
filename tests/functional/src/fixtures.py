"""Фикстуры для тестов."""
import asyncio
from asyncio.unix_events import _UnixSelectorEventLoop
from typing import Optional, Any

import aiohttp
import pytest
from aioredis import create_redis_pool, Redis
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import settings
from tests.functional.src.utils import HTTPResponse


@pytest.fixture
def event_loop(scope='session') -> _UnixSelectorEventLoop:
    """Переопределение event_loop.

    Сделано, чтобы не падали тесты при массовом запуске.
    """
    yield asyncio.get_event_loop()


@pytest.fixture(scope='session')
async def es_client() -> AsyncElasticsearch:
    """Определение Elastic Search клиента."""
    client = AsyncElasticsearch(hosts=settings.es_host)
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def redis_client() -> Redis:
    """Определение Redis клиента."""
    client = await create_redis_pool(
        (settings.REDIS_HOST, settings.REDIS_PORT), minsize=10, maxsize=20,
    )
    yield client


@pytest.fixture(scope='session')
async def session() -> aiohttp.ClientSession:
    """Определение aiohttp клиента."""
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session: aiohttp.ClientSession) -> Any:
    """Запрос в сервис."""
    async def inner(base_url: str, method: str, params: Optional[dict] = None) -> HTTPResponse:
        """Запрос в сервис."""
        params = params or {}
        async with session.get(base_url + method, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner
