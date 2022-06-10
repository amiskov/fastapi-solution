"""Тесты для API поиска персон.

Используемая ручка: API v1 /api/v1/persons/search?query='текст'.
"""
import http
from asyncio.unix_events import _UnixSelectorEventLoop
from typing import Callable

import pytest
from aiohttp import ClientSession
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fakedata.persons import fake_es_persons_index
from fixtures import es_client, event_loop, make_get_request, redis_client, session
from persons.fixtures import BASE_URL, setup
from settings import settings
from utils import clear_cache, create_index, remove_index


@pytest.mark.asyncio
async def test_persons_search_no_params(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /persons/ без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: выдача пустая.
    """
    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/search')

    # ==== Asserts ====
    assert response.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_persons_search_unknown(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест на вызов ручки /persons/ без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: выдача пустая.
    """
    # ==== Fake ====
    await fake_es_persons_index(es_client=es_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/search', params={'query': 'qwerty'})

    # ==== Asserts ====
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 0


@pytest.mark.asyncio
async def test_persons_search_one(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест поиска конкретного человека по ручке /persons/search.
    """
    # ==== Fake ====
    await fake_es_persons_index(es_client=es_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/search', params={'query': 'Vitaliy Rakitin'})

    # ==== Asserts ====
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body[0].get('name') == 'Vitaliy Rakitin'
    assert response.body[0].get('id') == '1'


@pytest.mark.asyncio
async def test_persons_search_many_cache(
        setup: None,
        session: ClientSession,
        es_client: AsyncElasticsearch,
        make_get_request: Callable,
        redis_client: Redis,
        event_loop: _UnixSelectorEventLoop,
) -> None:
    """
    Тест поиска множества человек по ручке /persons/search.

    Так же проверяется на работе кеша:
    * данные в базе меняются, количество подходящих людей уменьшается, но выдача остаётся прежней.

    1. Запрос данных без кеша (в базе 4 подходящих человека);
    2. Запрос данных с кешом (в базе 1 подходящий человек);
    3. Запрос данных после удаление кеша (в базе 1 подходящий человек);
    """
    def _check_body(response_body: list) -> None:
        assert len(response_body) == 4
        for item in response.body:
            assert item in [
                {'id': '1', 'name': 'Vitaliy Rakitin'},
                {'id': '5', 'name': 'Vitaliy Mcgee'},
                {'id': '8', 'name': 'Vitalii Yoder'},
                {'id': '10', 'name': 'Vitaliy Paul'},
            ]

    # ==== Fake 1 ====
    await fake_es_persons_index(es_client=es_client)

    # ==== Run 1 ====
    response = await make_get_request(base_url=BASE_URL, method='/search', params={'query': 'Vitaliy'})

    # ==== Asserts 1 ====
    assert response.status == http.HTTPStatus.OK
    _check_body(response.body)

    # ==== Fake 2 ====
    await remove_index(session=session, index='persons')
    await create_index(session=session, filename=settings.STATIC_ES_PERSONS_INDEX_PATH, index='persons')
    await fake_es_persons_index(es_client=es_client, limit=1)

    # ==== Run 2 ====
    response = await make_get_request(base_url=BASE_URL, method='/search', params={'query': 'Vitaliy'})

    # ==== Asserts 2 ====
    assert response.status == http.HTTPStatus.OK
    _check_body(response.body)

    # ==== Fake 3 ====
    await clear_cache(redis_client)

    # ==== Run 2 ====
    response = await make_get_request(base_url=BASE_URL, method='/search', params={'query': 'Vitaliy'})

    # ==== Asserts 3 ====
    assert response.status == http.HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body[0].get('name') == 'Vitaliy Rakitin'
    assert response.body[0].get('id') == '1'
