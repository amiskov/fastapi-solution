"""Загрузка Redis."""
from typing import Optional

from aioredis import Redis

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    """Загрузка Redis."""
    return redis
