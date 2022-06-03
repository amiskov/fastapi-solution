"""Тесты для API получения списка персон.

Используемая ручка: API v1 /api/v1/persons/.
"""
import pytest

from tests.functional.src.fakedata.persons import (
    fake_cache_persons_list_blank,
    fake_cache_persons_list_data,
    fake_es_persons_index,
)
from tests.functional.src.fixtures import es_client, make_get_request, redis_client, session
from tests.functional.src.persons.fixtures import setup, BASE_URL


@pytest.mark.asyncio
async def test_persons_list_cache_not_exists_es_index_blank(
        setup,
        es_client,
        make_get_request,
        redis_client
) -> None:
    """
    Тест на вызов ручки /persons/ без параметров.

    Уусловии: запрос отсутствует в кеше, Elastic Search index пустой.

    ОП: выдача пустая.
    """
    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/')

    # ==== Asserts ====
    assert response.status == 200
    assert len(response.body) == 0


@pytest.mark.asyncio
async def test_persons_list_cache_exists_es_index_blank(setup, es_client, make_get_request, redis_client) -> None:
    """
    Тест на вызов ручки /persons/ без параметров.

    Условие: запрос присутствует в кеше, Elastic Search index пустой.

    Проверяем 2 кейса:
    1. В кеше пустые данные -> ОР: выдача пустая;
    2. В кеше не пустые данные -> ОР: выдача соответствует данным в кеше;
    """
    # ======== Blank cache ========
    # ==== Fake ===
    await fake_cache_persons_list_blank(redis_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/')

    # ==== Asserts ====
    assert response.status == 200
    assert len(response.body) == 0

    # ======== Not blank cache ========
    # ==== Fake ===
    faked_persons_in_cache = await fake_cache_persons_list_data(redis_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/')

    # ==== Asserts ====
    assert response.status == 200
    assert response.body == faked_persons_in_cache


@pytest.mark.asyncio
async def test_persons_list_cache_blank_index_not_blank(
        setup,
        es_client,
        make_get_request,
        redis_client
) -> None:
    """
    Тест на вызов ручки /persons/ без параметров.

    Условие: запрос присутствует в кеше, Elastic Search index не пустой.
    Проверяем 2 кейса:
    1. В кеше пустые данные -> ОР: выдача пустая;
    2. В кеше не пустые данные (отличаются от данных в ES) -> ОР: выдача соответствует данным в кеше;
    """
    # ======== Blank cache ========
    # ==== Fake ===
    await fake_cache_persons_list_blank(redis_client=redis_client)
    faked_persons_in_es_index = await fake_es_persons_index(es_client=es_client)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/')

    # ==== Asserts ====
    assert response.status == 200
    assert len(faked_persons_in_es_index) > 0
    assert len(response.body) == 0

    # ======== Not Blank cache ========
    # ==== Fake ===
    faked_persons_in_cache = await fake_cache_persons_list_data(redis_client=redis_client, limit=5)

    # ==== Run ====
    response = await make_get_request(base_url=BASE_URL, method='/')

    # ==== Asserts ====
    assert response.status == 200
    assert response.body == faked_persons_in_cache
    assert len(response.body) != len(faked_persons_in_es_index)


@pytest.mark.asyncio
async def test_persons_list_cache_exists_not_blank_es_index_not_blank(
        setup,
        es_client,
        make_get_request,
        redis_client,
) -> None:
    """
    Тест на вызов ручки /persons/ без параметров.

    Условие: запрос отсутствует в кеше, Elastic Search index не пустой.
    Проверяем последовательно 2 кейса:
    1. В кеше нет данных -> ОР: выдача соответствует выдаче из Elastic Search;
    2. В Elastic Search данные поменялись -> выдача соответствует предыдущей выдаче из Elastic Search.
       (она сохранилась в кеш!)
    """
    # ==== Fake 1 ===
    faked_persons_in_es_index_1 = await fake_es_persons_index(es_client=es_client, limit=5)
    faked_persons_in_es_index_1_sorted = sorted(faked_persons_in_es_index_1, key=lambda x: x.get('id'), reverse=True)
    # ==== Run 1 ====
    response = await make_get_request(base_url=BASE_URL, method='/')

    # ==== Asserts 1 ====
    assert response.status == 200
    assert response.body == faked_persons_in_es_index_1_sorted

    # ==== Fake 2 ===
    faked_persons_in_es_index_2 = await fake_es_persons_index(es_client=es_client, limit=10)
    # ==== Run 2 ====
    response = await make_get_request(base_url=BASE_URL, method='/')

    # ==== Asserts 2 ====
    assert response.status == 200
    assert len(response.body) != len(faked_persons_in_es_index_2)
    assert response.body == faked_persons_in_es_index_1_sorted


@pytest.mark.asyncio
async def test_persons_list_pagination(
        setup,
        es_client,
        make_get_request,
        redis_client,
) -> None:
    """
    Тест на вызов ручки /persons/ с пагинацией.

    Данных в базе 7 элементов, пагинируемся последовательно по 5.
    Проверяем, что присутствие сторонних кешей не влияет на выдачу.
    """
    # ==== Fake 1 ===
    faked_persons_in_es_index_1 = await fake_es_persons_index(es_client=es_client, limit=7)
    await fake_cache_persons_list_data(redis_client=redis_client, limit=10)

    # ==== Run 1 ====
    response = await make_get_request(
        base_url=BASE_URL,
        method='/',
        params={'page[number]': 1, 'page[size]': 5},
    )

    # ==== Asserts 1 ====
    assert response.status == 200
    assert len(response.body) == 5
    for item in response.body:
        assert item in faked_persons_in_es_index_1

    # ==== Run 2 ====
    response = await make_get_request(
        base_url=BASE_URL,
        method='/',
        params={'page[number]': 2, 'page[size]': 5},
    )

    # ==== Asserts 2 ====
    assert response.status == 200
    assert len(response.body) == 2
    for item in response.body:
        assert item in faked_persons_in_es_index_1

    # ==== Run 3 ====
    response = await make_get_request(
        base_url=BASE_URL,
        method='/',
        params={'page[number]': 3, 'page[size]': 5},
    )

    # ==== Asserts 3 ====
    assert response.status == 200
    assert len(response.body) == 0
