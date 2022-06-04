from tests.functional.settings import settings
from tests.functional.src.fakedata.base import fake_es_index, fake_cache_list_data, get_cache_key_list, fake_cache_items
from tests.functional.src.fakedata.utils import fake_cache

fake_persons = [
    {"id": "1", "name": "Vitaliy Rakitin"},
    {"id": "2", "name": "Keira Liu"},
    {"id": "3", "name": "Matilda Beard"},
    {"id": "4", "name": "Erik Mercer"},
    {"id": "5", "name": "Vitaliy Mcgee"},
    {"id": "6", "name": "Carley Faulkner"},
    {"id": "7", "name": "Milly Padilla"},
    {"id": "8", "name": "Vitalii Yoder"},
    {"id": "9", "name": "Ariyah Robles"},
    {"id": "10", "name": "Vitaliy Paul"},
    {"id": "11", "name": "Oliver Valencia"},
]


async def fake_es_persons_index(
        es_client,
        limit: int = 50,
) -> list[dict]:
    """Наполнение данными индекс persons."""
    return await fake_es_index(es_client, index=settings.PERSONS_ES_INDEX, data=fake_persons, limit=limit)


async def fake_cache_persons_list_data(
        redis_client,
        page_size: int = 50,
        page_number: int = 1,
        limit: int = 50,
) -> list[dict]:
    """Наполнение кеша редис данными."""
    return await fake_cache_list_data(
        redis_client=redis_client,
        data=fake_persons,
        data_key='Person',
        page_size=page_size,
        page_number=page_number,
        limit=limit,
    )


async def fake_cache_persons_list_blank(
        redis_client,
        page_size: int = 50,
        page_number: int = 1,
) -> None:
    """Наполнение кеша редис данными."""
    await fake_cache(
        redis_client=redis_client,
        key=get_cache_key_list(data_key='Person', page_size=page_size, page_number=page_number),
        value=[],
    )


async def fake_cache_persons_items(redis_client) -> None:
    """Наполнение кеша редис персоналиями по id."""
    await fake_cache_items(
        redis_client=redis_client,
        data=fake_persons,
        data_key='Person',
    )
