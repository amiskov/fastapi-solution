"""Тесты для API получения списка фильмов по id персоны.

Используемая ручка: API v1 /api/v1/persons/:id/film.
"""

from asyncio.unix_events import _UnixSelectorEventLoop
from typing import Callable

import pytest
from aiohttp import ClientSession
from aioredis import Redis
from elasticsearch import AsyncElasticsearch

from tests.functional.src.fakedata.persons import fake_es_films_index, fake_es_persons_index
from tests.functional.src.fixtures import es_client, event_loop, make_get_request, redis_client, session
from tests.functional.src.persons.fixtures import BASE_URL, setup
from tests.functional.src.utils import remove_index


@pytest.mark.asyncio
async def test_persons_films_blank(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /persons/:id/film без параметров.

    Условии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: 404.
    """
    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/1/film')

    # ==== Asserts ====
    assert response.status == 404


@pytest.mark.asyncio
async def test_persons_films_with_cache(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /persons/:id/film без параметров.

    Условии: запрос отсутствует в кеше, Elastic Search index не пустой.
    Делается 2 запроса подряд. (после 1-го запроса очищается Elastic Search)

    ОП: в обоих случаях выдача из 4 фильмов (после 1 запроса фильмы закешировались).
    """
    def _asserts() -> None:
        assert response.status == 200
        assert len(response.body) == 5
        for item in response.body:
            assert item.get('id') in ['11', '12', '14', '15', '16']

    # ==== Fake ====
    await fake_es_persons_index(es_client=es_client)
    await fake_es_films_index(es_client=es_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/1/film')

    # ==== Asserts ====
    _asserts()

    # ==== Clear ES ====
    await remove_index(session=session, index='persons')
    await remove_index(session=session, index='movies')

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/1/film')

    # ==== Asserts ====
    _asserts()
