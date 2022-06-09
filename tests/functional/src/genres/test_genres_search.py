"""Тесты для API поиска жанров.

Используемая ручка: API v1 /api/v1/genres/search?query='текст'.
"""

import os
from asyncio.unix_events import _UnixSelectorEventLoop
from typing import Callable

import pytest
from aiohttp import ClientSession
from aioredis import Redis
from elasticsearch import AsyncElasticsearch

from tests.functional.src.fakedata.genres import fake_es_genres_index
from tests.functional.src.fixtures import es_client, event_loop, make_get_request, redis_client, session
from tests.functional.src.genres.fixtures import BASE_URL, setup
from tests.functional.src.utils import clear_cache, create_index, remove_index

current_dir = os.path.dirname(__file__)
static_dir = os.path.join(current_dir, "..", "static")

@pytest.mark.asyncio
async def test_genres_search_no_params(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /genres/ без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: выдача пустая.
    """
    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/search')

    # ==== Asserts ====
    assert response.status == 400


@pytest.mark.asyncio
async def test_genres_search_unknown(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /genres/ без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: выдача пустая.
    """
    # ==== Fake ====
    await fake_es_genres_index(es_client=es_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/search', params={'query': 'qwerty'})

    # ==== Asserts ====
    assert response.status == 200
    assert len(response.body) == 0


@pytest.mark.asyncio
async def test_genres_search_one(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест поиска конкретного человека по ручке /genres/search.
    """
    # ==== Fake ====
    await fake_es_genres_index(es_client=es_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/search', params={'query': 'Triller'})

    # ==== Asserts ====
    assert response.status == 200
    assert len(response.body) == 1
    assert response.body[0].get('name') == 'thriller'
    assert response.body[0].get('id') == '2'


@pytest.mark.asyncio
async def test_genres_search_many_cache(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест поиска множества человек по ручке /genres/search.

    Так же проверяется на работе кеша:
    * данные в базе меняются, количество подходящих людей уменьшается, но выдача остаётся прежней.

    1. Запрос данных без кеша (в базе 4 подходящих человека);
    2. Запрос данных с кешом (в базе 1 подходящий человек);
    3. Запрос данных после удаление кеша (в базе 1 подходящий человек);
    """
    def _check_body(response_body: list) -> None:
        assert len(response_body) == 3
        for item in response.body:
            assert item in [
                {'id': '1', 'name': 'horror', 'description': 'scary movie'},
                {'id': '2', 'name': 'thriller', 'description': 'scary films'},
                {'id': '7', 'name': 'scary genre', 'description': None},
            ]

    # ==== Fake 1 ====
    await fake_es_genres_index(es_client=es_client)

    # ==== Run 1 ====
    response = await make_get_request(base_url=BASE_URL, method='/search', params={'query': 'scary'})

    # ==== Asserts 1 ====
    assert response.status == 200
    _check_body(response.body)

    # ==== Fake 2 ====
    await remove_index(session=session, index='genres')
    await create_index(session=session, filename=static_dir + '/create_genres_index.json', index='genres')
    await fake_es_genres_index(es_client=es_client, limit=1)

    # ==== Run 2 ====
    response = await make_get_request(base_url=BASE_URL, method='/search', params={'query': 'scary'})

    # ==== Asserts 2 ====
    assert response.status == 200
    _check_body(response.body)

    # ==== Fake 3 ====
    await clear_cache(redis_client)

    # ==== Run 2 ====
    response = await make_get_request(base_url=BASE_URL, method='/search', params={'query': 'scary'})

    # ==== Asserts 3 ====
    assert response.status == 200
    assert len(response.body) == 1
    assert response.body[0] == {'id': '1', 'name': 'horror', 'description': 'scary movie'}
