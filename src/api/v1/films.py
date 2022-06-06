"""API фильмов."""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from errors import FilmNotFoundException, MissedQueryParameterException
from models.film import FilmAPIResponse, map_film_response
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get('/search', response_model=list[FilmAPIResponse])
async def films_search(
        film_service: FilmService = Depends(get_film_service),
        query: str = None,
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
) -> list[FilmAPIResponse]:
    """Возвращает список фильмов для отправки по API, соответствующий критериям поиска."""
    if not query:
        raise MissedQueryParameterException(parameter='query')
    search_result = await film_service.get_search_result(
        query=query,
        page_size=page_size,
        page_number=page_number
    )
    return [map_film_response(f) for f in search_result]


@router.get('/', response_model=list[FilmAPIResponse])
async def films_list(
        film_service: FilmService = Depends(get_film_service),
        sort: Optional[str] = '-imdb_rating',
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
        filter_genre: str = Query(None, alias='filter[genre]'),
) -> list[FilmAPIResponse]:
    """Возвращает список фильмов для отправки по API, соответствующий критериям фильтрации."""
    films = await film_service.get_list(
        sort=sort,
        page_size=page_size,
        page_number=page_number,
        genre_id=filter_genre,
    )
    return [map_film_response(film) for film in films]


@router.get('/{film_id}', response_model=FilmAPIResponse)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service),
) -> FilmAPIResponse:
    """Детализация кинопроизведения.

    Args:
        film_id (str):
        film_service (FilmService, optional):

    Returns:
        FilmAPIResponse:
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise FilmNotFoundException()

    return map_film_response(film)
