import asyncio

import aioredis
from settings import settings
from utils import logger, backoff

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT


@backoff(service="Redis")
async def ping_redis() -> None:
    redis = await aioredis.create_redis_pool((REDIS_HOST, REDIS_PORT))
    await redis.ping()
    logger.info('Successfully connected to Redis.')
    redis.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(ping_redis())
