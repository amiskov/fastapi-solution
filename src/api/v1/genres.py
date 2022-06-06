"""API жанров."""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from errors import GenreNotFoundException, MissedQueryParameterException
from models.genre import GenreAPIResponse
from services.genre import GenresService, get_genres_service

router = APIRouter()


@router.get(
    '/',
    response_model=list[GenreAPIResponse],
    summary="Список жанров.",
    description="Полный список всех персон.",
    response_description="Список всех персон.",
    tags=['Список жанров'],
)
async def genres_list(
        genre_service: GenresService = Depends(get_genres_service),
        sort: Optional[str] = '-id',
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
) -> list[GenreAPIResponse]:
    """Возвращает список жанров для отправки по API, соответствующий критериям фильтрации."""
    genres = await genre_service.get_list(
        sort=sort,
        page_size=page_size,
        page_number=page_number,
    )
    return [GenreAPIResponse(**item.dict()) for item in genres]


@router.get(
    '/search',
    response_model=list[GenreAPIResponse],
    summary="Поиск по жанрам.",
    description="Полнотекстовый поиск по жанрам.",
    response_description="Список всех жанров.",
    tags=['Поиск по жанрам'],
)
async def genres_search(
        genre_service: GenresService = Depends(get_genres_service),
        query: str = None,
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
) -> list[GenreAPIResponse]:
    """Возвращает список жанров для отправки по API, соответствующий критериям поиска."""
    if not query:
        raise MissedQueryParameterException(parameter='query')

    search_result = await genre_service.get_search_result(
        query=query,
        page_size=page_size,
        page_number=page_number,
    )

    return [GenreAPIResponse(**item.dict()) for item in search_result]


@router.get(
    '/{genre_id}',
    response_model=GenreAPIResponse,
    summary="Детализация жанра.",
    description="Детализация жанра по id.",
    response_description="Подробная информация о жанре (наименование и описание).",
    tags=['Детализация жанра'],
)
async def genre_details(
        genre_id: str,
        genre_service: GenresService = Depends(get_genres_service),
) -> GenreAPIResponse:
    """Детализация жанра.

    Args:
        genre_id (str):
        genre_service (GenresService, optional):

    Returns:
        GenreAPIResponse:
    """
    genre = await genre_service.get_by_id(genre_id)

    if not genre:
        raise GenreNotFoundException()

    return GenreAPIResponse(**genre.dict())
