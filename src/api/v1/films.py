"""API фильмов."""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from api.v1.paging_params import PagingParams
from errors import FilmNotFoundException, MissedQueryParameterException
from models.film import FilmAPIResponse, map_film_response
from services.film import FilmService, get_film_service

router = APIRouter()


@router.get(
    '/',
    response_model=list[FilmAPIResponse],
    summary='Список всех кинопроизведений.',
    description='Полный список всех кинопроизведениям.',
    response_description='Список всех кинопроизведений.',
    tags=['Список всех элементов'],
)
async def films_list(
        film_service: FilmService = Depends(get_film_service),
        paging_params: PagingParams = Depends(),
        sort: Optional[str] = '-imdb_rating',
        filter_genre: str = Query(None, alias='filter[genre]'),
) -> list[FilmAPIResponse]:
    """Возвращает список фильмов для отправки по API, соответствующий критериям фильтрации."""
    films = await film_service.get_list(
        sort=sort,
        page_size=paging_params.page_size,
        page_number=paging_params.page_number,
        genre_id=filter_genre,
    )
    return [map_film_response(film) for film in films]


@router.get(
    '/search',
    response_model=list[FilmAPIResponse],
    summary='Поиск кинопроизведений.',
    description='Полнотекстовый поиск по кинопроизведениям.',
    response_description='Список подходящих кинопроизведений.',
    tags=['Полнотекстовый поиск'],
)
async def films_search(
        film_service: FilmService = Depends(get_film_service),
        query: str = None,
        paging_params: PagingParams = Depends(),
) -> list[FilmAPIResponse]:
    """Возвращает список фильмов для отправки по API, соответствующий критериям поиска."""
    if not query:
        raise MissedQueryParameterException(parameter='query')
    search_result = await film_service.get_search_result(
        query=query,
        page_size=paging_params.page_size,
        page_number=paging_params.page_number,
    )
    return [map_film_response(f) for f in search_result]


@router.get(
    '/{film_id}',
    response_model=FilmAPIResponse,
    summary='Получение фильма по id.',
    description='Получение полной информации о фильме по id.',
    response_description='Детализация фильма..',
    tags=['Получение даннх по id'],
)
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
