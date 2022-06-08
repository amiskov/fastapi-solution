from dataclasses import dataclass
from typing import Optional

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

SERVICE_URL = 'http://127.0.0.1:8000'


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


# `scope='session'` means "apply fixture before all tests,
# and terminate it after all tests"
@pytest.fixture(scope='session')
async def es_client():
    """Creates an ES client before and tears it down after the test."""
    client = AsyncElasticsearch(hosts='127.0.0.1:9200')
    # Everything before `yield` will be executed before tests,
    yield client
    # and everything after the `yield` will be executed after the tests.
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str,
                    params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        url = SERVICE_URL + '/api/v1' + method  # в боевых системах старайтесь так не делать!
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
