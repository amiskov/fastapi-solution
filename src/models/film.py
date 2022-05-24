"""Описание модели кинопроизведения."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from models.base_model_mixin import ConfigOverrideMixin
from models.genre import Genre
from models.person import Actor, Writer


class Film(BaseModel, ConfigOverrideMixin):
    """Модель кинопроизведения."""

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
