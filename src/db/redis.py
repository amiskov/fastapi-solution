"""TODO: оформить."""
from typing import Optional

from aioredis import Redis

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """TODO: оформить."""
    return redis
