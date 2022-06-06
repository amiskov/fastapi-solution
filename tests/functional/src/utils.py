"""Утилиты для тестов."""
from dataclasses import dataclass

from aiohttp import ClientSession
from aioredis import Redis
from multidict import CIMultiDictProxy

from tests.functional.settings import settings
from tests.functional.src.errors import ESCreateIndexError, ESRemoveIndexError, ESResourceAlreadyExistsError


@dataclass
class HTTPResponse:
    """Описание ответа от сервиса."""

    body: dict
    headers: CIMultiDictProxy[str]
    status: int


async def _create_index(session: ClientSession, data: str, index: str) -> None:
    """
    Создание индекса в ElasticSearch.

    Args:
        session: Сессия;
        data: Данные, по которым создаётся индекс;
        index: наименование индекса.

    Returns:
        None.
    """
    headers = {
        'Content-Type': 'application/json',
    }
    async with session.put(f'{settings.es_host}/{index}', data=data, headers=headers) as response:
        if response.status != 200:
            data = await response.json()
            error_type = data.get('error', {}).get('type')
            if error_type == 'resource_already_exists_exception':
                raise ESResourceAlreadyExistsError
            raise ESCreateIndexError


async def remove_index(session: ClientSession, index: str) -> None:
    """
    Удаление индекса в ElasticSearch.

    Args:
        session: Сессия;
        index: наименование индекса.

    Returns:
        None.
    """
    async with session.delete(f'{settings.es_host}/{index}') as response:
        if response.status not in (200, 404):
            raise ESRemoveIndexError


async def create_index(session: ClientSession, index: str, filename: str) -> None:
    """
    Создание индекса в ElasticSearch.

    Если такой индекс существует, то он будет очищен и создан заново.

    Args:
        session: Сессия;
        index: наименование индекса;
        filename: файл с данными, по которым создаётся индекс.

    Returns:
        None.
    """
    with open(filename, 'r') as file:
        data = file.read()
        try:
            await _create_index(session=session, data=data, index=index)
        except ESResourceAlreadyExistsError:
            await remove_index(session=session, index=index)
            await _create_index(session=session, data=data, index=index)


async def clear_cache(redis_client: Redis) -> None:
    """
    Очистка кеша.

    Args:
        redis_client: клиент для Redis.

    Returns:
        None.
    """
    for keys in await redis_client.scan():
        if isinstance(keys, list):
            for key in keys:
                await redis_client.delete(key)
