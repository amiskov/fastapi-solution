"""
Общая фикстура дл тестов на ручку /api/v1/persons/.
"""
import pytest
from aioredis import Redis
from aiohttp import ClientSession

from tests.functional.settings import settings
from tests.functional.src.utils import clear_cache, create_index, remove_index

BASE_URL = settings.service_url + '/api/v1/persons'


@pytest.fixture
async def setup(session: ClientSession, redis_client: Redis) -> None:
    """
    Насройка теста.

    Подготавливаем индекс в ElasticSearch.
    TODO: Посмотреть возможность переделать на setup_function и teardown_function.
    """
    await create_index(session=session, filename='../static/create_persons_index.json', index='persons')
    await create_index(session=session, filename='../static/create_movies_index.json', index='movies')
    await clear_cache(redis_client)
    yield
    await remove_index(session=session, index='persons')
    await remove_index(session=session, index='movies')
    await clear_cache(redis_client)
