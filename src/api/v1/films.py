"""API фильмов."""
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

import models.film
from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    """
    Модель кинопроизведения для API Response.
    """

    id: str
    title: str
    imdb_rating: float
    description: Optional[str]
    actors: list
    writers: list
    directors: str  # TODO: should be a list
    genre: list


def map_film_model(f: models.film.Film) -> Film:
    return Film(id=f.id,
                title=f.title,
                imdb_rating=f.imdb_rating,
                description=f.description,
                actors=f.actors,
                directors=f.director,
                writers=f.writers,
                genre=f.genre)


@router.get('/search', response_model=list[Film])
async def films_search(
        film_service: FilmService = Depends(get_film_service),
        query: str = None,
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
) -> list[Film]:
    if not query:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail='Query parameter is required.')
    search_result = await film_service.get_search_result(
        query=query,
        page_size=page_size,
        page_number=page_number
    )
    if not search_result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Films not found.')
    films = [map_film_model(f) for f in search_result]
    return films


@router.get('/', response_model=list[Film])
async def films_list(
        film_service: FilmService = Depends(get_film_service),
        sort: Optional[str] = '-imdb_rating',
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
        filter_genre: str = Query(None, alias='filter[genre]')
) -> list[Film]:
    films = await film_service.get_list(
        sort=sort,
        page_size=page_size,
        page_number=page_number,
        filter_genre=filter_genre
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='films not found')
    films_resp = [map_film_model(f) for f in films]
    return films_resp


@router.get('/{film_id}', response_model=Film)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service),
) -> Film:
    """Детализация кинопроизведения.

    Args:
        film_id (str):
        film_service (FilmService, optional):

    Returns:
        Film:
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')

    return map_film_model(film)
