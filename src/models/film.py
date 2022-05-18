"""Описание модели кинопроизведения."""
from typing import Any

import orjson
from pydantic import BaseModel


def orjson_dumps(v: Any, *, default: Any) -> None:
    """JSON dumps."""
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel):
    """Модель кинопроизведения."""

    id: str
    title: str
    description: str

    class Config:
        """Конфиги кинопроизведения."""

        json_loads = orjson.loads
        json_dumps = orjson_dumps
