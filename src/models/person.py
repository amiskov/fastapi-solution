from pydantic import BaseModel
from pydantic.fields import Field
from models.base_mixin import BaseMixin


class Person(BaseModel, BaseMixin):
    id: str
    name: str


class Actor(Person):
    # films: list = Field(title="Фильмы с актёром")
    pass


class Director(Person):
    # films: list = Field(title="Снятые режиссёром фильмы")
    pass


class Writer(Person):
    # films: list = Field(title="Фильмы по сценарию")
    pass
