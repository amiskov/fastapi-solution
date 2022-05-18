from pydantic import BaseModel, Field
from models.base_mixin import BaseMixin


class Genre(BaseModel, BaseMixin):
    id: str
    name: str = Field(title="Название жанра")
    description: str = Field(title="Описание жанра")
    # TODO: What is genre popularity?
    popularity: float = Field(title="Популярность жанра")
