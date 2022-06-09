"""Фейковые данные для ручек /api/v1/genres."""

from tests.functional.settings import settings
from tests.functional.src.fakedata.base import fake_cache_items, fake_cache_list_data, fake_es_index, get_cache_key_list
from tests.functional.src.fakedata.utils import fake_cache

fake_genres = [
    {'id': '1', 'name': 'horror', 'description': 'scary movie'},
    {'id': '2', 'name': 'thriller', 'description': 'scary films'},
    {'id': '3', 'name': 'comedy', 'description': None},
    {'id': '4', 'name': 'action', 'description': None},
    {'id': '5', 'name': 'biopic', 'description': None},
    {'id': '6', 'name': 'doc', 'description': None},
    {'id': '7', 'name': 'scary genre', 'description': None},
    {'id': '8', 'name': 'mystery', 'description': None},
    {'id': '9', 'name': 'drama', 'description': None},
    {'id': '10', 'name': 'romantic', 'description': None},
    {'id': '11', 'name': 'fantasy', 'description': None},
]


async def fake_es_genres_index(
        es_client,
        limit: int = 50,
) -> list[dict]:
    """Наполнение данными индекс persons."""
    return await fake_es_index(es_client, index=settings.GENRES_ES_INDEX, data=fake_genres, limit=limit)


async def fake_cache_genres_list_data(
        redis_client,
        page_size: int = 50,
        page_number: int = 1,
        limit: int = 50,
) -> list[dict]:
    """Наполнение кеша редис данными."""
    return await fake_cache_list_data(
        redis_client=redis_client,
        data=fake_genres,
        data_key='Genre',
        page_size=page_size,
        page_number=page_number,
        limit=limit,
    )


async def fake_cache_genres_list_blank(
        redis_client,
        page_size: int = 50,
        page_number: int = 1,
) -> None:
    """Наполнение кеша редис данными."""
    await fake_cache(
        redis_client=redis_client,
        key=get_cache_key_list(data_key='Genre', page_size=page_size, page_number=page_number),
        value=[],
    )


async def fake_cache_genres_items(redis_client) -> None:
    """Наполнение кеша редис жанрами по id."""
    await fake_cache_items(
        redis_client=redis_client,
        data=fake_genres,
        data_key='Genre',
    )
