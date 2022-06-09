import asyncio
import logging

import aiohttp

from tests.functional.settings import settings

ES_URL = settings.es_host

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestElastic")


async def ping_elastic(url: str, sleep_time: int = 1) -> None:
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.head(url):
                    logger.info('Successfully connected to Elastic.')
                    exit(0)  # everything is fine
            except Exception as e:
                logger.error(e)
                msg = f'Error connecting ES. Trying again ' \
                      f'in {sleep_time} seconds...',
                logger.error(msg)
                await asyncio.sleep(sleep_time)
            else:
                exit(1)  # something abnormal happened


loop = asyncio.get_event_loop()
loop.run_until_complete(ping_elastic(ES_URL))
