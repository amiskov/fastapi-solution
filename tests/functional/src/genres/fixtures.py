"""
Общая фикстура дл тестов на ручку /api/v1/persons/.
"""
import os

import pytest
from aiohttp import ClientSession
from aioredis import Redis

from tests.functional.settings import settings
from tests.functional.src.utils import clear_cache, create_index, remove_index

BASE_URL = settings.service_url + '/api/v1/genres'
INDEX = 'genres'

current_dir = os.path.dirname(__file__)
static_dir = os.path.join(current_dir, "..", "static")

@pytest.fixture
async def setup(session: ClientSession, redis_client: Redis) -> None:
    """
    Насройка теста.

    Подготавливаем индекс в ElasticSearch.
    TODO: Посмотреть возможность переделать на setup_function и teardown_function.
    """
    await create_index(session=session, filename=static_dir + '/create_genres_index.json', index=INDEX)
    await clear_cache(redis_client)
    yield
    await remove_index(session=session, index=INDEX)
    await clear_cache(redis_client)
