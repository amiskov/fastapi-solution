"""Описание модели кинопроизведения."""
from typing import Any, Optional

import orjson

from pydantic import BaseModel, Field
from models.base_mixin import ConfigOverrideMixin
from models.person import Actor, Writer


def orjson_dumps(v: Any, *, default: Any) -> str:
    """JSON dumps."""
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel, ConfigOverrideMixin):
    """Модель кинопроизведения."""
    # TODO: There should be Movie and Series types but for now in our DB
    # there are only `movie` type. So we go with only Film for now.
    id: str
    title: str = Field(title="Название фильма")
    description: Optional[str] = Field(title="Описание фильма")
    imdb_rating: float = Field(title="Рейтинг IMDB")
    director: str = Field(title="Режиссёры")  # TODO: should be a list
    actors: list[Actor] = Field(title="Актёры")
    writers: list[Writer] = Field(title="Сценаристы")
    genre: list[str] = Field(title="Жанры")  # TODO: should be a list of Genre
    file_path: Optional[str] = Field(title="Ссылка на файл")
    # TODO: add `created` to Elastic
    # created: str = Field(title="Дата создания фильма")
    # TODO: We don't have `age_restriction` in our DB.
    # age_restriction: int = Field(title="Возрастной ценз")
