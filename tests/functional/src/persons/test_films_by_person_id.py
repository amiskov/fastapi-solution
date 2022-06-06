"""Тесты для API получения списка фильмов по id персоны.

Используемая ручка: API v1 /api/v1/persons/:id/film.
"""
import pytest

from tests.functional.src.fakedata.persons import (
    fake_cache_persons_list_blank,
    fake_cache_persons_list_data,
    fake_es_persons_index,
    fake_cache_persons_items, fake_es_films_index)
from tests.functional.src.fixtures import es_client, make_get_request, redis_client, session, event_loop
from tests.functional.src.persons.fixtures import setup, BASE_URL


@pytest.mark.asyncio
async def test_persons_films_blank(
        setup,
        es_client,
        make_get_request,
        redis_client,
        event_loop,
) -> None:
    """
    Тест на вызов ручки /persons/:id/film без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: 404.
    """
    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/1/film')

    # ==== Asserts ====
    assert response.status == 404


@pytest.mark.asyncio
async def test_persons_films(
        setup,
        es_client,
        make_get_request,
        redis_client,
        event_loop,
) -> None:
    """
    Тест на вызов ручки /persons/:id/film без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: 404.
    """
    # ==== Fake ====
    await fake_es_films_index(es_client=es_client)
    await fake_es_persons_index(es_client=es_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/1/film')

    # ==== Asserts ====
    assert response.status == 200
    assert len(response.body) == 2

