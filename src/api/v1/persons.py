"""API персон."""
from typing import Optional

from fastapi import APIRouter, Depends

from api.v1.paging_params import PagingParams
from errors import MissedQueryParameterException, PersonNotFoundException
from models.film import FilmAPIResponse, map_film_response
from models.person import PersonAPIResponse
from services.film import FilmService, get_film_service
from services.person import PersonsService, get_persons_service

router = APIRouter()


@router.get(
    '/',
    response_model=list[PersonAPIResponse],
    summary='Список персон.',
    description='Полный список всех персон.',
    response_description='Список всех персон.',
    tags=['Список всех элементов'],
)
async def persons_list(
        person_service: PersonsService = Depends(get_persons_service),
        sort: Optional[str] = '-id',
        paging_params: PagingParams = Depends(),
) -> list[PersonAPIResponse]:
    """Возвращает список персон для отправки по API, соответствующий критериям фильтрации."""
    persons = await person_service.get_list(
        sort=sort,
        page_size=paging_params.page_size,
        page_number=paging_params.page_number,
    )
    return [PersonAPIResponse(**item.dict()) for item in persons]


@router.get(
    '/search',
    response_model=list[PersonAPIResponse],
    summary='Поиск по персоналиям.',
    description='Полнотекстовый поиск по персоналиям.',
    response_description='Список персон.',
    tags=['Полнотекстовый поиск'],
)
async def persons_search(
        person_service: PersonsService = Depends(get_persons_service),
        query: str = None,
        paging_params: PagingParams = Depends(),
) -> list[PersonAPIResponse]:
    """Возвращает список персон для отправки по API, соответствующий критериям поиска."""
    if not query:
        raise MissedQueryParameterException(parameter='query')

    search_result = await person_service.get_search_result(
        query=query,
        page_size=paging_params.page_size,
        page_number=paging_params.page_number,
    )
    return [PersonAPIResponse(**item.dict()) for item in search_result]


@router.get(
    '/{person_id}',
    response_model=PersonAPIResponse,
    summary='Детализация персоны.',
    description='Детализация персоны по id..',
    response_description='Подробная информация о персоне (полное имя).',
    tags=['Получение даннх по id'],
)
async def person_details(
        person_id: str,
        person_service: PersonsService = Depends(get_persons_service),
) -> PersonAPIResponse:
    """Детализация персоны.

    Args:
        person_id (str):
        person_service (PersonsService):

    Returns:
        PersonAPIResponse:
    """
    person = await person_service.get_by_id(person_id)

    if not person:
        raise PersonNotFoundException()

    return PersonAPIResponse(**person.dict())


@router.get(
    '/{person_id}/film',
    response_model=list[FilmAPIResponse],
    summary='Поиск фильма по персоне.',
    description='Поиск всех фильмов, где участвовал конкретный человек (по id персоны).',
    response_description='Список фильмов.',
    tags=['Поиск фильма по персоне'],
)
async def films_by_person_id(
        person_id: str,
        person_service: PersonsService = Depends(get_persons_service),
        paging_params: PagingParams = Depends(),
        film_service: FilmService = Depends(get_film_service),
) -> PersonAPIResponse:
    """Фильмы по персоне.

    Args:
        person_id (str):
        paging_params (PagingParams):
        person_service (PersonsService):
        film_service (FilmService):

    Returns:
        PersonAPIResponse:
    """
    person = await person_service.get_by_id(person_id)

    if not person:
        raise PersonNotFoundException()

    films = await film_service.get_search_result(
        query=person.name,
        page_size=paging_params.page_size,
        page_number=paging_params.page_number,
        fields=['actors_names', 'writers_names', 'director'],
    )
    return [map_film_response(film) for film in films]
