"""Описание модели жанра."""
from pydantic import BaseModel, Field

from models.base_model_mixin import ConfigOverrideMixin


class Genre(BaseModel, ConfigOverrideMixin):
    """Модель жанра."""

    id: str
    name: str = Field(title='Название жанра')
    description: str = Field(title='Описание жанра')
    # TODO: What is genre popularity?
    # popularity: float = Field(title='Популярность жанра')


class GenreAPIResponse(BaseModel, ConfigOverrideMixin):
    """Модель жанра для API Response."""

    id: str
    name: str = Field(title='Название жанра')
    description: str = Field(title='Описание жанра')
