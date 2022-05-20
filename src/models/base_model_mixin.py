from typing import Any

import orjson


def orjson_dumps(v: Any, *, default: Any) -> str:
    """JSON dumps."""
    return orjson.dumps(v, default=default).decode()


class ConfigOverrideMixin:
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
