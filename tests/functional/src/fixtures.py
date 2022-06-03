from typing import Optional

import aiohttp
import pytest
from aioredis import create_redis_pool
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import settings
from tests.functional.src.utils import HTTPResponse


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=settings.es_host)
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def redis_client():
    client = await create_redis_pool(
        (settings.REDIS_HOST, settings.REDIS_PORT), minsize=10, maxsize=20
    )
    yield client


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
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
