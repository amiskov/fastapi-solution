"""Caching API queries."""
from functools import wraps
from typing import Callable, Optional, Type, Union

import orjson
from aioredis import Redis
from pydantic import BaseModel
from pydantic.json import pydantic_encoder

CachedData = Union[BaseModel, list[BaseModel]]

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """Return the Redis instance."""
    return redis


def gen_key(model_name: str,
            fn_name: str,
            args: tuple,
            kwargs: dict) -> str:
    """Return a caching key based on model, method, and its arguments."""
    args_part = list(args[1:])
    kwargs_part = [f'{k}={v}' for k, v in kwargs.items() if v is not None]
    key_parts = [model_name, fn_name] + args_part + kwargs_part
    return ':'.join(key_parts)


def cache(model_class: Type[BaseModel] = None,
          is_compound: bool = False,
          ttl: int = 60) -> Callable:
    """Return decorator for caching the result of calling `fn`."""

    def _cache(fn: Callable) -> Callable:
        @wraps(fn)
        async def _wrapper(*args, **kwargs) -> CachedData:
            key = gen_key(model_class.__name__, fn.__name__, args, kwargs)
            cached_data = await redis.get(key)
            if cached_data:
                if is_compound:
                    parsed_cache = orjson.loads(cached_data)
                    data = [model_class(**d) for d in parsed_cache]
                else:
                    data = model_class.parse_raw(cached_data)
            else:
                data = await fn(*args, **kwargs)
                data_json = orjson.dumps(data, default=pydantic_encoder)
                await redis.set(key, data_json, expire=ttl)
            return data

        return _wrapper

    return _cache
