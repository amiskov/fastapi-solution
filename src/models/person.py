from pydantic import BaseModel
from pydantic.fields import Field
from models.base_mixin import BaseMixin


class Person(BaseModel, BaseMixin):
    id: str
    full_name: str


class Actor(Person):
    films: list = Field(title="Фильмы с актёром")


class Director(Person):
    films: list = Field(title="Снятые режиссёром фильмы")


class Writer(Person):
    films: list = Field(title="Фильмы по сценарию")
