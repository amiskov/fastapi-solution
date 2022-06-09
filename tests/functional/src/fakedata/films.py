"""Фейковые данные для ручек /api/v1/films."""

from fakedata.base import fake_cache_items, fake_cache_list_data, \
    fake_es_index, get_cache_key_list
from fakedata.utils import fake_cache
from settings import settings
import pathlib
import orjson

fake_films = [
    {'id': '2a090dde-f688-46fe-a9f4-b781a985275e',
     'title': 'Star Wars: Knights of the Old Republic',
     'imdb_rating': 9.6,
     'description': '',
     'creation_date': None,
     'actors': [],
     'writers': [],
     'director': [],
     'genre': []
     },
    {
        "id": "c241874f-53d3-411a-8894-37c19d8bf010",
        "title": "Star Wars SC 38 Reimagined",
        "imdb_rating": 9.5,
        "description": "",
        "creation_date": None,
        "actors": [],
        "writers": [],
        'director': [],
        "genre": []
    },
    {
        "id": "05d7341e-e367-4e2e-acf5-4652a8435f93",
        "title": "The Secret World of Jeffree Star",
        "imdb_rating": 9.5,
        "description": "",
        "creation_date": None,
        "actors": [],
        "writers": [],
        "director": [],
        "genre": []
    },
    {
        "id": "c49c1df9-6d06-47b7-87db-d96190901fa4",
        "title": "Ringo Rocket Star and His Song for Yuri Gagarin",
        "imdb_rating": 9.4,
        "description": "",
        "creation_date": None,
        "actors": [],
        "writers": [],
        "director": [],
        "genre": []
    },
    {
        "id": "c71db79a-6978-46da-9b89-43a92ebfceac",
        "title": "Kirby Super Star",
        "imdb_rating": 9.2,
        "description": "",
        "creation_date": None,
        "actors": [],
        "writers": [],
        "director": [],
        "genre": []
    },
]


async def fake_es_films_index(
        es_client,
        limit: int = 5,
) -> list[dict]:
    """Наполнение данными индекс persons."""
    return await fake_es_index(es_client, index=settings.MOVIES_INDEX,
                               data=fake_films, limit=limit)


async def fake_cache_films_list_data(
        redis_client,
        page_size: int = 50,
        page_number: int = 1,
        limit: int = 5,
) -> list[dict]:
    """Наполнение кеша редис данными."""
    return await fake_cache_list_data(
        redis_client=redis_client,
        data=fake_films,
        data_key='Film',
        page_size=page_size,
        page_number=page_number,
        limit=limit,
        sort='-imdb_rating',
    )


async def fake_cache_films_list_blank(
        redis_client,
        page_size: int = 50,
        page_number: int = 1,
) -> None:
    """Наполнение кеша редис данными."""
    await fake_cache(
        redis_client=redis_client,
        key=get_cache_key_list(
            data_key='Film',
            page_size=page_size,
            page_number=page_number,
            sort='-imdb_rating',
        ),
        value=[],
    )


async def fake_cache_films_items(redis_client) -> None:
    """Наполнение кеша редис жанрами по id."""
    await fake_cache_items(
        redis_client=redis_client,
        data=fake_films,
        data_key='Film',
    )
