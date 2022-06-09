import asyncio
import logging

import aioredis

from tests.functional.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestRedis")

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT


async def ping_redis(sleep_time: int = 1) -> None:
    while True:
        try:
            redis = await aioredis.create_redis_pool((REDIS_HOST, REDIS_PORT))
            await redis.ping()
            logger.info('Successfully connected to Redis.')
            exit(0)
        except Exception as e:
            logger.error(e)
            msg = f'Error connecting Redis. Trying again ' \
                  f'in {sleep_time} seconds...',
            logger.error(msg)
            await asyncio.sleep(sleep_time)
        else:
            exit(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(ping_redis())
