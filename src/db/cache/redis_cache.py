"""Caching API queries."""
from dataclasses import dataclass
from typing import Callable, Optional, Type

import orjson
from aioredis import Redis
from pydantic import BaseModel
from pydantic.json import pydantic_encoder

from db.cache.base import BaseCache

DEFAULT_TIME_TO_LIVE = 60 * 5

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """Return the Redis instance."""
    return redis


@dataclass
class RedisCache(BaseCache):
    redis_client: Redis
    model_class: Type[BaseModel]
    ttl: int = DEFAULT_TIME_TO_LIVE

    async def get_entity_from_cache_or_db(
            self,
            get_entity_from_db_fn: Callable,
            entity_id: str
    ) -> Optional[BaseModel]:
        """
        Get the entity from cache (e.g. Film details).
        If it's not in cache, then use `get_entity_from_db_fn` function
        and `entity_id` to get the entity from the original data source.
        """
        key = self._get_caching_key(
            get_entity_from_db_fn.__name__,
            entity_id=entity_id,
        )
        cached_data = await self.redis_client.get(key)
        if cached_data:
            data = cached_data
        else:
            data_raw = await get_entity_from_db_fn(entity_id)
            data = orjson.dumps(data_raw, default=pydantic_encoder)
            await self.redis_client.set(key, data, expire=self.ttl)
        return self.model_class.parse_raw(data)

    async def get_list_from_cache_or_db(
            self,
            get_list_from_db_fn: Callable,
            **kwargs
    ) -> list[BaseModel]:
        """
        Get list of entities from cache (e.g. list of Films).
        If they're not cached, then get them from the original data source
        with `get_list_from_db_fn` and `**kwargs`.
        """
        key = self._get_caching_key(get_list_from_db_fn.__name__, **kwargs)
        cached_data = await self.redis_client.get(key)
        if cached_data:
            data = cached_data
        else:
            data_raw = await get_list_from_db_fn(**kwargs)
            data = orjson.dumps(data_raw, default=pydantic_encoder)
            await self.redis_client.set(key, data, expire=self.ttl)
        return [self.model_class(**entity) for entity in orjson.loads(data)]

    def _get_caching_key(self, fn_name: str, **kwargs) -> str:
        """Return a caching key based on model, method, and its parameters."""
        model_name = self.model_class.__name__
        params = [f'{k}={v}' for k, v in kwargs.items() if v is not None]
        caching_key_parts = [model_name, fn_name] + params
        return '/'.join(caching_key_parts)
