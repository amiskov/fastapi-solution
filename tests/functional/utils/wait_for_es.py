import asyncio
import logging
import os
import sys

import aiohttp
from functional.settings import settings

# Tweak `PYTHONPATH`
tests_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(tests_path)

ES_URL = settings.es_host + "3"

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
