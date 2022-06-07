"""Сервис загрузки кинопроизведений."""
from dataclasses import dataclass
from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.cache.redis import get_redis
from db.data_providers.elastic import get_elastic
from db.data_providers.films import FilmsDataProvider
from services.base_service import BaseService


@dataclass
class FilmService(BaseService):
    db: FilmsDataProvider


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    """
    Сервис по загрузке кинопроизведений.

    Args:
        redis:
        elastic:

    Returns:
        FilmService:
    """
    return FilmService(
        db=FilmsDataProvider(es_client=elastic, es_index='movies'),
    )
