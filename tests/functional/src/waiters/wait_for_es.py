import asyncio
import aiohttp
from settings import settings
from utils import logger, backoff

ES_URL = settings.ELASTIC_URL


if not ES_URL:
    logger.error('Elastic Search URL is not defined.')
    exit(1)


@backoff(service="ElasticSearch")
async def ping_elastic(url: str, sleep_time: int = 1) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.head(url):
            logger.info('Successfully connected to Elastic.')


loop = asyncio.get_event_loop()
loop.run_until_complete(ping_elastic(ES_URL, sleep_time=10))
