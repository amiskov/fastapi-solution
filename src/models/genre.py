"""Описание модели жанра."""
from typing import Optional

from pydantic import BaseModel, Field

from models.base_model_mixin import ConfigOverrideMixin


class Genre(BaseModel, ConfigOverrideMixin):
    """Модель жанра."""

    id: str
    name: str = Field(title='Название жанра')
    description: Optional[str] = Field(title='Описание жанра')


class GenreAPIResponse(BaseModel, ConfigOverrideMixin):
    """Модель жанра для API Response."""

    id: str
    name: str = Field(title='Название жанра')
    description: Optional[str] = Field(title='Описание жанра')
