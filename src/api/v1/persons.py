"""API персон."""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from errors import MissedQueryParameterException, PersonNotFoundException
from models.person import PersonAPIResponse
from services.person import PersonsService, get_persons_service
from src.models.film import FilmAPIResponse, map_film_response
from src.services.film import FilmService, get_film_service

router = APIRouter()


@router.get('/search', response_model=list[PersonAPIResponse])
async def persons_search(
        person_service: PersonsService = Depends(get_persons_service),
        query: str = None,
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
) -> list[PersonAPIResponse]:
    """Возвращает список персон для отправки по API, соответствующий критериям поиска."""
    if not query:
        raise MissedQueryParameterException(parameter='query')

    search_result = await person_service.get_search_result(
        query=query,
        page_size=page_size,
        page_number=page_number,
    )
    return [PersonAPIResponse(**item.dict()) for item in search_result]


@router.get('/', response_model=list[PersonAPIResponse])
async def persons_list(
        person_service: PersonsService = Depends(get_persons_service),
        sort: Optional[str] = '-id',
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
) -> list[PersonAPIResponse]:
    """Возвращает список персон для отправки по API, соответствующий критериям фильтрации."""
    persons = await person_service.get_list(
        sort=sort,
        page_size=page_size,
        page_number=page_number,
    )
    return [PersonAPIResponse(**item.dict()) for item in persons]


@router.get('/{person_id}', response_model=PersonAPIResponse)
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


@router.get('/{person_id}/film', response_model=list[FilmAPIResponse])
async def films_by_person_id(
        person_id: str,
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
        person_service: PersonsService = Depends(get_persons_service),
        film_service: FilmService = Depends(get_film_service),
) -> PersonAPIResponse:
    """Фильмы по персоне.

    Args:
        person_id (str):
        page_size (int):
        page_number (int):
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
        page_size=page_size,
        page_number=page_number,
        fields=['actors_names', 'writers_names', 'director'],
    )
    return [map_film_response(film) for film in films]
