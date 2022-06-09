"""Фейковые данные для ручек /api/v1/persons."""

from datetime import datetime

from fakedata.base import fake_cache_items, fake_cache_list_data, fake_es_index, get_cache_key_list
from fakedata.utils import fake_cache
from settings import settings

fake_persons = [
    {'id': '1', 'name': 'Vitaliy Rakitin'},
    {'id': '2', 'name': 'Keira Liu'},
    {'id': '3', 'name': 'Matilda Beard'},
    {'id': '4', 'name': 'Erik Mercer'},
    {'id': '5', 'name': 'Vitaliy Mcgee'},
    {'id': '6', 'name': 'Carley Faulkner'},
    {'id': '7', 'name': 'Milly Padilla'},
    {'id': '8', 'name': 'Vitalii Yoder'},
    {'id': '9', 'name': 'Ariyah Robles'},
    {'id': '10', 'name': 'Vitaliy Paul'},
    {'id': '11', 'name': 'Oliver Valencia'},
]

fake_movies = [
    {
        'id': '11',
        'title': 'Фильм 1',
        'description': None,
        'imdb_rating': 0.5,
        'creation_date': str(datetime.now().date()),
        'genre': [],
        'director': [],
        'actors_names': '',
        'writers_names': '',
        'actors': [fake_persons[2]],
        'writers': [fake_persons[0]],
    },
    {
        'id': '12',
        'title': 'Фильм 2',
        'description': None,
        'imdb_rating': 0.6,
        'creation_date': str(datetime.now().date()),
        'genre': [],
        'director': [],
        'actors_names': '',
        'writers_names': '',
        'actors': [fake_persons[0]],
        'writers': [fake_persons[5]],
    },
    {
        'id': '13',
        'title': 'Фильм 3',
        'description': None,
        'imdb_rating': 0.8,
        'creation_date': str(datetime.now().date()),
        'genre': [],
        'director': [],
        'actors_names': '',
        'writers_names': '',
        'actors': [fake_persons[1], fake_persons[2]],
        'writers': [fake_persons[3], fake_persons[4]],
    },
    {
        'id': '14',
        'title': 'Фильм 4',
        'description': None,
        'imdb_rating': 0.9,
        'creation_date': str(datetime.now().date()),
        'genre': [],
        'director': [],
        'actors_names': '',
        'writers_names': '',
        'actors': [fake_persons[0], fake_persons[2]],
        'writers': [fake_persons[0], fake_persons[1], fake_persons[2]],
    },
    {
        'id': '15',
        'title': 'Фильм 5',
        'description': None,
        'imdb_rating': 1.0,
        'creation_date': str(datetime.now().date()),
        'genre': [],
        'director': [],
        'actors_names': '',
        'writers_names': '',
        'actors': [fake_persons[1], fake_persons[2]],
        'writers': [fake_persons[0], fake_persons[0]],
    },
    {
        'id': '16',
        'title': 'Фильм 5',
        'description': None,
        'imdb_rating': 1.0,
        'creation_date': str(datetime.now().date()),
        'genre': [],
        'director': [],
        'actors_names': fake_persons[0].get('name'),
        'writers_names': '',
        'actors': [],
        'writers': [],
    },
]


def update_names(names_field: str, objects_field: str) -> None:
    """Обновление имён персон в кинопроизведениях."""
    for movie in fake_movies:
        for person in movie.get(objects_field, []):
            name = person.get('name', None)
            if name not in movie[names_field]:
                movie[names_field] += ', ' + name


update_names(names_field='actors_names', objects_field='actors')
update_names(names_field='writers_names', objects_field='writers')


async def fake_es_persons_index(
        es_client,
        limit: int = 50,
) -> list[dict]:
    """Наполнение данными индекс persons."""
    return await fake_es_index(es_client, index=settings.PERSONS_ES_INDEX, data=fake_persons, limit=limit)


async def fake_es_films_index(
        es_client,
        limit: int = 50,
) -> list[dict]:
    """Наполнение данными индекс persons."""
    return await fake_es_index(es_client, index=settings.MOVIES_INDEX, data=fake_movies, limit=limit)


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


# async def fake_cache_persons_films(redis_client) -> None:
#     """Наполнение кеша редис персоналиями по id."""
#     await fake_cache_items(
#         redis_client=redis_client,
#         data=fake_persons,
#         data_key='Films',
#     )
