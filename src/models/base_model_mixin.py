"""Переопределение умолчаний модели базовой Pydantic."""

from typing import Any

import orjson


def orjson_dumps(v: Any, *, default: Any) -> str:
    """JSON dumps."""
    return orjson.dumps(v, default=default).decode()


class ConfigOverrideMixin:
    """Перегружает методы из базовой модели Pydantic."""

    class Config:
        """Более производительные методы для обработки JSON."""

        json_loads = orjson.loads
        json_dumps = orjson_dumps
