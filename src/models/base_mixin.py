import orjson


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseMixin:
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
