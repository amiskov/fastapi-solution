"""Тесты для API получения жанров по id.

Используемая ручка: API v1 /api/v1/genres/:id.
"""
import http
from asyncio.unix_events import _UnixSelectorEventLoop
from typing import Callable

import pytest
from aiohttp import ClientSession
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fakedata.genres import fake_cache_genres_items, fake_es_genres_index, fake_genres
from fixtures import es_client, event_loop, make_get_request, redis_client, session
from genres.fixtures import BASE_URL, setup


@pytest.mark.asyncio
async def test_genres_item_by_id_blank(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /genres/:id/ без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: 404.
    """
    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method=f'/{fake_genres[0]["id"]}/')

    # ==== Asserts ====
    assert response.status == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_genres_item_by_id_cache_exists(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /genres/:id/ без параметров.

    Условие: запрос присутствует в кеше.
    """
    # ==== Fake ====
    await fake_cache_genres_items(redis_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method=f'/{fake_genres[0]["id"]}/')

    # ==== Asserts ====
    assert response.status == http.HTTPStatus.OK
    assert response.body == fake_genres[0]


@pytest.mark.asyncio
async def test_genres_item_by_id_cache_not_exists(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /genres/:id/ без параметров.

    Условие: запрос присутствует в кеше.
    """
    # ==== Fake ====
    await fake_es_genres_index(es_client=es_client)

    # ==== Run ====
    response_1 = await make_get_request(base_url=BASE_URL, method=f'/{fake_genres[0]["id"]}/')
    response_2 = await make_get_request(base_url=BASE_URL, method='/404/')

    # ==== Asserts ====
    assert response_1.status == 200
    assert response_1.body == fake_genres[0]
    assert response_2.status == 404
