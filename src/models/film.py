from pydantic import BaseModel, Field, HttpUrl
from models.base_mixin import BaseMixin
from datetime import datetime
from models.person import Director, Actor, Writer
from models.genre import Genre


class Film(BaseModel, BaseMixin):
    id: str
    title: str = Field(title="Название фильма")
    description: str = Field(title="Описание фильма")
    creation_date: datetime = Field(title="Дата создания фильма")
    age_restriction: int = Field(title="Возрастной ценз")
    directors: list[Director] = Field(title="Режиссёры")
    actors: list[Actor] = Field(title="Актёры")
    writers: list[Writer] = Field(title="Сценаристы")
    genres: list[Genre] = Field(title="Жанры")
    file_url: HttpUrl = Field(title="Ссылка на файл")


class Movie:
    pass


class Series:
    pass
