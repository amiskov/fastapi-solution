"""Caching API queries."""
from functools import wraps
from pprint import pprint
from typing import Callable, Optional, Union

import orjson
from aioredis import Redis
from pydantic import BaseModel
from pydantic.json import pydantic_encoder

DEFAULT_TIME_TO_LIVE = 60 * 5

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """Return the Redis instance."""
    return redis


# def cache_details(
#         model_class: Type[BaseModel],
#         ttl: int = DEFAULT_TIME_TO_LIVE,
# ) -> Callable:
#     """
#     Provide a caching decorator for a single API resource of `model_class`.
#
#     E.g. for a Film details.
#     """
#
#     def restore_data(raw_data: bytes) -> Optional[model_class]:
#         return model_class.parse_raw(raw_data)
#
#     return _cache(model_class, restore_data, ttl)
#
#
# def cache_list(
#         model_class: Type[BaseModel],
#         ttl: int = DEFAULT_TIME_TO_LIVE,
# ) -> Callable:
#     """
#     Provide a caching decorator for a list of API resources of `model_class`.
#
#     E.g. for a list of Films.
#     """
#
#     def restore_data(raw_data: bytes) -> list[model_class]:
#         parsed_cache = orjson.loads(raw_data)
#         return [model_class(**d) for d in parsed_cache]
#
#     return _cache(model_class, restore_data, ttl)


def gen_key(
        fn_name: str,
        key_args: tuple,
        key_kwargs: dict,
) -> str:
    """Return a caching key based on model, method, and its parameters."""
    args_part = list(key_args[1:])
    kwargs_part = [f'{k}={v}' for k, v in key_kwargs.items() if v is not None]
    key_parts = [fn_name] + args_part + kwargs_part
    return ':'.join(key_parts)


def _get_caching_key(model_name, fn_name: str, **kwargs) -> str:
    """Return a caching key based on model, method, and its parameters."""
    params = [f'{k}={v}' for k, v in kwargs.items() if v is not None]
    caching_key_parts = [model_name, fn_name] + params
    return '/'.join(caching_key_parts)


def cache(ttl: int = DEFAULT_TIME_TO_LIVE) -> Callable:
    """Return decorator for caching the result of calling `fn`."""

    def __cache(fn: Callable) -> Callable:

        @wraps(fn)
        async def _wrapper(
                *args,
                **kwargs,
        ) -> Union[BaseModel, list[BaseModel]]:
            key = gen_key(fn.__qualname__, args, kwargs)
            cached_data = await redis.get(key)
            if cached_data:
                data = dict(orjson.loads(cached_data))
                print("FROM CACHE!!!!!!!!!!!!!!")
                pprint(data)
            else:
                data = await fn(*args, **kwargs)
                data_json = orjson.dumps(data, default=pydantic_encoder)
                await redis.set(key, data_json, expire=ttl)
                print("FROM ELASTIC!!!!!!!!!!!!!!")
                print(data)
            return data

        return _wrapper

    return __cache
