"""Тесты для API поиска фильмов.

Используемая ручка: API v1 /api/v1/films/search?query='текст'.
"""

import http
from asyncio.unix_events import _UnixSelectorEventLoop
from typing import Callable

import pytest
from aiohttp import ClientSession
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fakedata.films import fake_es_films_index, fake_films
from films.fixtures import BASE_URL, setup
from fixtures import es_client, event_loop, make_get_request, redis_client, session
from settings import settings
from utils import clear_cache, create_index, remove_index


@pytest.mark.asyncio
async def test_films_search_no_params(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /films/ без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: выдача пустая.
    """
    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/search')

    # ==== Asserts ====
    assert response.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_films_search_unknown(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /films/ без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: выдача пустая.
    """
    # ==== Fake ====
    await fake_es_films_index(es_client=es_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/search',
                                      params={'query': 'qwerty'})

    # ==== Asserts ====
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 0


@pytest.mark.asyncio
async def test_films_search_one(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест поиска конкретного человека по ручке /films/search.
    """
    # ==== Fake ====
    await fake_es_films_index(es_client=es_client)

    # ==== Run ====
    response = await make_get_request(
        base_url=BASE_URL,
        method='/search',
        params={'query': 'Yuri Gagarin'},
    )

    # ==== Asserts ====
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body[0].get('title') == fake_films[3]['title']
    assert response.body[0].get('id') == fake_films[3]['id']


@pytest.mark.asyncio
async def test_films_search_many_cache(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест поиска нескольких фильмов по ручке /films/search.
    """

    def _check_body(response_body: list) -> None:
        assert len(response_body) == 2
        for item in response.body:
            assert item in fake_films[0:2]

    # ==== Fake 1 ====
    await fake_es_films_index(es_client=es_client)

    # ==== Run 1 ====
    response = await make_get_request(
        base_url=BASE_URL,
        method='/search',
        params={'query': 'Star Wars'}
    )

    # ==== Asserts 1 ====
    assert response.status == http.HTTPStatus.OK
    _check_body(response.body)

    # ==== Fake 2 ====
    await remove_index(session=session, index=settings.MOVIES_INDEX)
    await create_index(session=session,
                       filename=settings.STATIC_ES_MOVIES_INDEX_PATH,
                       index=settings.MOVIES_INDEX)
    await fake_es_films_index(es_client=es_client, limit=1)

    # ==== Run 2 ====
    response = await make_get_request(
        base_url=BASE_URL,
        method='/search',
        params={'query': 'Star Wars'}
    )

    # ==== Asserts 2 ====
    assert response.status == http.HTTPStatus.OK
    _check_body(response.body)

    # ==== Fake 3 ====
    await clear_cache(redis_client)

    # ==== Run 2 ====
    response = await make_get_request(
        base_url=BASE_URL,
        method='/search',
        params={'query': 'Star Wars'}
    )

    # ==== Asserts 3 ====
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 1
