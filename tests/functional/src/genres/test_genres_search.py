"""Тесты для API получения списка персон.

Используемая ручка: API v1 /api/v1/genres/search?query='текст'.
"""


import pytest

from tests.functional.src.fakedata.genres import fake_es_genres_index
from tests.functional.src.fixtures import es_client, make_get_request, redis_client, session, event_loop
from tests.functional.src.genres.fixtures import setup, BASE_URL
from tests.functional.src.utils import remove_index, create_index, clear_cache


@pytest.mark.asyncio
async def test_genres_search_no_params(
        setup,
        es_client,
        make_get_request,
        redis_client,
        event_loop,
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
        setup,
        es_client,
        make_get_request,
        redis_client,
        event_loop,
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
        setup,
        es_client,
        make_get_request,
        redis_client,
        event_loop,
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
        setup,
        es_client,
        make_get_request,
        redis_client,
        session,
        event_loop,
) -> None:
    """
    Тест поиска множества человек по ручке /genres/search.

    Так же проверяется на работе кеша:
    * данные в базе меняются, количество подходящих людей уменьшается, но выдача остаётся прежней.

    1. Запрос данных без кеша (в базе 4 подходящих человека);
    2. Запрос данных с кешом (в базе 1 подходящий человек);
    3. Запрос данных после удаление кеша (в базе 1 подходящий человек);
    """
    def _check_body(response_body):
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
    await create_index(session=session, filename='../static/create_genres_index.json', index='genres')
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
