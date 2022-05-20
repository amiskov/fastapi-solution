"""API фильмов."""
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    """
    Модель кинопроизведения.
    """

    id: str
    title: str
    imdb_rating: float
    description: Optional[str]
    actors: list
    writers: list
    directors: str  # TODO: should be a list
    genre: list


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

    return Film(id=film.id,
                title=film.title,
                description=film.description,
                actors=film.actors,
                directors=film.director,
                writers=film.writers,
                genre=film.genre)


@router.get('/', response_model=list[Film])
async def films_list(
        film_service: FilmService = Depends(get_film_service),
        sort: Optional[str] = "-imdb_rating",
        page_size: int = Query(50, alias="page[size]", ge=1),
        page_number: int = Query(1, alias="page[number]", ge=1)
) -> list[Film]:
    film_resp = await film_service.get_list(
        sort=sort,
        page_size=page_size,
        page_number=page_number)
    if not film_resp:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='films not found')
    films = []
    for f in film_resp:
        films.append(Film(id=f.id,
                          title=f.title,
                          imdb_rating=f.imdb_rating,
                          description=f.description,
                          actors=f.actors,
                          directors=f.director,
                          writers=f.writers,
                          genre=f.genre))
    return films
