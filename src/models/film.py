from typing import Optional

from pydantic import BaseModel, Field, HttpUrl
from models.base_mixin import ConfigOverrideMixin
from datetime import datetime
from models.person import Director, Actor, Writer
from models.genre import Genre


class Film(BaseModel, ConfigOverrideMixin):
    # TODO: There should be Movie and Series types but for now in our DB
    # there are only `movie` type. So we go with only Film for now.
    id: str
    title: str = Field(title="Название фильма")
    description: Optional[str] = Field(title="Описание фильма")
    imdb_rating: float = Field(title="Рейтинг IMDB")
    # creation_date: datetime = Field(title="Дата создания фильма")
    # TODO: We don't have `age_restriction` in our DB.
    # age_restriction: int = Field(title="Возрастной ценз")
    director: str = Field(title="Режиссёры")  # TODO: should be a list
    actors: list[Actor] = Field(title="Актёры")
    writers: list[Writer] = Field(title="Сценаристы")
    genre: list[str] = Field(title="Жанры")  # TODO: should be a list of Genre
    file_url: HttpUrl = Field(title="Ссылка на файл")


class Movie:
    pass


class Series:
    pass
