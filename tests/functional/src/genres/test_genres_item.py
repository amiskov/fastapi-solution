"""Тесты для API получения жанров по id.

Используемая ручка: API v1 /api/v1/genres/:id.
"""
import pytest

from tests.functional.src.fakedata.genres import (
    fake_es_genres_index,
    fake_cache_genres_items,
)
from tests.functional.src.fixtures import es_client, make_get_request, redis_client, session, event_loop
from tests.functional.src.genres.fixtures import setup, BASE_URL


@pytest.mark.asyncio
async def test_genres_item_by_id_blank(
        setup,
        es_client,
        make_get_request,
        redis_client,
        event_loop,
) -> None:
    """
    Тест на вызов ручки /genres/:id/ без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: 404.
    """
    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/1/')

    # ==== Asserts ====
    assert response.status == 404


@pytest.mark.asyncio
async def test_genres_item_by_id_cache_exists(
        setup,
        es_client,
        make_get_request,
        redis_client,
        event_loop,
) -> None:
    """
    Тест на вызов ручки /genres/:id/ без параметров.

    Условие: запрос присутствует в кеше.
    """
    # ==== Fake ====
    await fake_cache_genres_items(redis_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/1/')

    # ==== Asserts ====
    assert response.status == 200
    assert response.body == {'description': 'scary movie', 'id': '1', 'name': 'horror'}


@pytest.mark.asyncio
async def test_genres_item_by_id_cache_not_exists(
        setup,
        es_client,
        make_get_request,
        redis_client,
        event_loop,
) -> None:
    """
    Тест на вызов ручки /genres/:id/ без параметров.

    Условие: запрос присутствует в кеше.
    """
    # ==== Fake ====
    await fake_es_genres_index(es_client=es_client)

    # ==== Run ====
    response_1 = await make_get_request(base_url=BASE_URL, method='/1/')
    response_2 = await make_get_request(base_url=BASE_URL, method='/404/')

    # ==== Asserts ====
    assert response_1.status == 200
    assert response_1.body == {'description': 'scary movie', 'id': '1', 'name': 'horror'}
    assert response_2.status == 404
