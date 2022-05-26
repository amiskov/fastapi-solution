"""Модели для актёров, режиссёров и сценаристов."""
from pydantic import BaseModel

from models.base_model_mixin import ConfigOverrideMixin


class Person(BaseModel, ConfigOverrideMixin):
    """Базовая модель для актеров, режиссёров и сценаристов."""

    id: str
    name: str


class PersonAPIResponse(BaseModel, ConfigOverrideMixin):
    """Модель персон для API Response."""

    id: str
    name: str


class Actor(Person):
    """Модель актёра."""

    # TODO: retrieve films from Elastic
    # films: list = Field(title='Фильмы с актёром')


class Director(Person):
    """Модель режиссёра."""

    # TODO: retrieve films from Elastic
    # films: list = Field(title='Снятые режиссёром фильмы')


class Writer(Person):
    """Модель сценариста."""

    # TODO: retrieve films from Elastic
    # films: list = Field(title='Фильмы по сценарию')
