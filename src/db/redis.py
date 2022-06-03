"""Caching API queries."""
from functools import wraps
from typing import Callable, Optional, Type, Union

import orjson
from aioredis import Redis
from pydantic import BaseModel
from pydantic.json import pydantic_encoder

DEFAULT_TIME_TO_LIVE = 60 * 5

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """Return the Redis instance."""
    return redis


def cache_details(
        model_class: Type[BaseModel],
        ttl: int = DEFAULT_TIME_TO_LIVE,
) -> Callable:
    """
    Provide a caching decorator for a single API resource of `model_class`.

    E.g. for a Film details.
    """

    def restore_data(raw_data: bytes) -> Optional[model_class]:
        return model_class.parse_raw(raw_data)

    return _cache(model_class, restore_data, ttl)


def cache_list(
        model_class: Type[BaseModel],
        ttl: int = DEFAULT_TIME_TO_LIVE,
) -> Callable:
    """
    Provide a caching decorator for a list of API resources of `model_class`.

    E.g. for a list of Films.
    """

    def restore_data(raw_data: bytes) -> list[model_class]:
        parsed_cache = orjson.loads(raw_data)
        return [model_class(**d) for d in parsed_cache]

    return _cache(model_class, restore_data, ttl)


def gen_key(
        model_name: str,
        fn_name: str,
        key_args: tuple,
        key_kwargs: dict,
) -> str:
    """Return a caching key based on model, method, and its parameters."""
    args_part = list(key_args[1:])
    kwargs_part = [f'{k}={v}' for k, v in key_kwargs.items() if v is not None]
    key_parts = [model_name, fn_name] + args_part + kwargs_part
    return ':'.join(key_parts)


def _cache(
        model_class: Type[BaseModel],
        data_restorer: Callable,
        ttl: int,
) -> Callable:
    """Return decorator for caching the result of calling `fn`."""

    def __cache(fn: Callable) -> Callable:

        @wraps(fn)
        async def _wrapper(
                *args,
                **kwargs,
        ) -> Union[BaseModel, list[BaseModel]]:
            key = gen_key(model_class.__name__, fn.__name__, args, kwargs)
            print(f"RESTORE BY KEY: {key}")
            cached_data = await redis.get(key)
            if cached_data:
                print(f"DATA EXITS")
                data = data_restorer(cached_data)
            else:
                print(f"LOAD DATA")
                data = await fn(*args, **kwargs)
                data_json = orjson.dumps(data, default=pydantic_encoder)
                await redis.set(key, data_json, expire=ttl)
            return data

        return _wrapper

    return __cache
