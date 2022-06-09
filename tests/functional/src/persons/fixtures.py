"""
Общая фикстура дл тестов на ручку /api/v1/persons/.
"""
import pytest
from aiohttp import ClientSession
from aioredis import Redis
from settings import settings
from utils import clear_cache, create_index, remove_index

BASE_URL = settings.SERVICE_URL + '/api/v1/persons'


@pytest.fixture
async def setup(session: ClientSession, redis_client: Redis) -> None:
    """
    Насройка теста.

    Подготавливаем индекс в ElasticSearch.
    TODO: Посмотреть возможность переделать на setup_function и teardown_function.
    """
    await create_index(session=session, filename=settings.STATIC_ES_PERSONS_INDEX_PATH, index='persons')
    await create_index(session=session, filename=settings.STATIC_ES_MOVIES_INDEX_PATH, index='movies')
    await clear_cache(redis_client)
    yield
    await remove_index(session=session, index='persons')
    await remove_index(session=session, index='movies')
    await clear_cache(redis_client)
