"""Caching API queries."""
from dataclasses import dataclass
from typing import Callable, Optional, Type, Union

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
    """Caches queries with Redis."""

    redis_client: Redis
    model_class: Type[BaseModel]
    ttl: int = DEFAULT_TIME_TO_LIVE

    async def get_from_cache_or_db(
            self,
            get_from_db: Callable,
            **kwargs,
    ) -> Union[Optional[BaseModel], list[BaseModel]]:
        """Retrieve the data from the data source for further caching."""
        key = self._get_caching_key(get_from_db, **kwargs)
        cached_data = await self.redis_client.get(key)
        if cached_data:
            data = cached_data
        else:
            data_raw = await get_from_db(**kwargs)
            data = orjson.dumps(data_raw, default=pydantic_encoder)
            await self.redis_client.set(key, data, expire=self.ttl)

        d = orjson.loads(data)
        if isinstance(d, dict):
            return self.model_class(**d)
        elif isinstance(d, list):
            return [self.model_class(**entity) for entity in d]
        else:
            return None

    def _get_caching_key(self, fn: Callable, **kwargs) -> str:
        """Return a caching key based on model, method, and its parameters."""
        params = [f'{k}={v}' for k, v in kwargs.items() if v is not None]
        caching_key_parts = [self.model_class.__name__, fn.__name__] + params
        print(':'.join(caching_key_parts))
        return ':'.join(caching_key_parts)
