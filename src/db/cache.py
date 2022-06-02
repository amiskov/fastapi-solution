from abc import ABC, abstractmethod
from typing import Callable, Optional, Type

import orjson
from aioredis import Redis
from pydantic import BaseModel
from pydantic.json import pydantic_encoder


class Cache(ABC):
    @abstractmethod
    def get_entity_from_cache_or_db(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_list_from_cache_or_db(self, *args, **kwargs):
        pass


DEFAULT_TIME_TO_LIVE = 60 * 5


class CacheWithRedis(Cache):
    def __init__(
            self,
            redis: Redis,
            caching_model_class: Type[BaseModel],
            ttl: int = DEFAULT_TIME_TO_LIVE
    ) -> None:
        self.redis = redis
        self.model_class = caching_model_class
        self.ttl = ttl

    async def get_entity_from_cache_or_db(
            self,
            get_entity_fn: Callable,
            entity_id: str
    ) -> Optional[BaseModel]:

        """
        Retrieve the entity from cache (e.g. Film details).
        If there's no entity in cache, then use `get_entity_fn` function
        and `entity_id` to get the entity from the original data source.
        """

        key = self._get_caching_key(get_entity_fn.__name__, (entity_id,), {})
        cached_data = await self.redis.get(key)
        if cached_data:
            data = self.model_class.parse_raw(cached_data)
        else:
            data = await get_entity_fn(entity_id)
            data_json = orjson.dumps(data, default=pydantic_encoder)
            await self.redis.set(key, data_json, expire=self.ttl)
        return data

    async def get_list_from_cache_or_db(
            self,
            get_list_fn: Callable,
            **kwargs
    ) -> list[dict]:
        """
        Get list of entities from cache (e.g. list of Films) or get them from
        the original data source with `get_list_fn` and `**kwargs`.
        """

        key = self._get_caching_key(get_list_fn.__name__, tuple(), kwargs)
        cached_data = await self.redis.get(key)
        if cached_data:
            data = orjson.loads(cached_data)
        else:
            data = await get_list_fn(**kwargs)
            data_json = orjson.dumps(data, default=pydantic_encoder)
            await self.redis.set(key, data_json, expire=self.ttl)
        return data

    def _get_caching_key(
            self,
            fn_name: str,
            key_args: tuple,
            key_kwargs: dict,
    ) -> str:
        """Return a caching key based on model, method, and its parameters."""
        args_part = list(key_args)
        kwargs_part = [f'{k}={v}' for k, v in key_kwargs.items() if
                       v is not None]
        model_name = self.model_class.__name__
        key_parts = [model_name, fn_name] + args_part + kwargs_part
        return '/'.join(key_parts)
