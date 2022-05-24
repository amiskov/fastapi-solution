"""Описание модели кинопроизведения."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from models.base_model_mixin import ConfigOverrideMixin
from models.genre import Genre
from models.person import Actor, Writer


class Film(BaseModel, ConfigOverrideMixin):
    """Модель кинопроизведения."""

    # TODO: There should be Movie and Series types but for now in our DB
    # there are only `movie` type. So we go with only Film for now.
    id: str
    title: str = Field(title='Название фильма')
    description: Optional[str] = Field(title='Описание фильма')
    created: datetime = Field(title='Дата создания фильма')
    imdb_rating: float = Field(title='Рейтинг IMDB')
    director: list[str] = Field(title='Режиссёры')
    actors: list[Actor] = Field(title='Актёры')
    writers: list[Writer] = Field(title='Сценаристы')
    genre: list[Genre] = Field(title='Жанры')
    file_path: Optional[str] = Field(title='Ссылка на файл')
    # TODO: We don't have `age_restriction` in our DB.
    # age_restriction: int = Field(title='Возрастной ценз')


class FilmAPIResponse(BaseModel, ConfigOverrideMixin):
    """Модель кинопроизведения для API Response."""

    id: str
    title: str
    imdb_rating: float
    description: Optional[str]
    created: datetime
    actors: list
    writers: list
    directors: list[str]
    genre: list[Genre]


def map_film_response(f: Film) -> FilmAPIResponse:
    """
    Возвращает модель фильма для выдачи по API.
    """
    return FilmAPIResponse(id=f.id,
                           title=f.title,
                           imdb_rating=f.imdb_rating,
                           description=f.description,
                           created=f.created,
                           actors=f.actors,
                           directors=f.director,
                           writers=f.writers,
                           genre=f.genre)
