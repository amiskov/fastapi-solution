"""API жанров."""
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from models.genre import GenreAPIResponse
from services.genre import GenresService, get_genres_service

router = APIRouter()


@router.get('/search', response_model=list[GenreAPIResponse])
async def genres_search(
        genre_service: GenresService = Depends(get_genres_service),
        query: str = None,
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
) -> list[GenreAPIResponse]:
    """Возвращает список жанров для отправки по API, соответствующий критериям поиска."""
    if not query:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Query parameter is required.',
        )

    search_result = await genre_service.get_search_result(
        query=query,
        page_size=page_size,
        page_number=page_number,
    )

    if not search_result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Genres not found.',
        )

    return [GenreAPIResponse(**item.dict()) for item in search_result]


@router.get('/', response_model=list[GenreAPIResponse])
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

    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='genres not found',
        )

    return [GenreAPIResponse(**item.dict()) for item in genres]


@router.get('/{genre_id}', response_model=GenreAPIResponse)
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
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='genre not found',
        )

    return GenreAPIResponse(**genre.dict())
