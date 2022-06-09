"""Сервис загрузки жанров."""
from dataclasses import dataclass
from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from core.config import settings
from db.cache.redis import RedisCache, get_redis
from db.data_providers.elastic import get_elastic
from db.data_providers.genres import GenresDataProvider
from models.genre import Genre
from services.base_service import BaseService

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


@dataclass
class GenresService(BaseService):
    """Сервис загрузки жанров."""

    db: GenresDataProvider
    cache: RedisCache


@lru_cache()
def get_genres_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenresService:
    """
    Сервис по загрузке жанров.

    Args:
        redis:
        elastic:

    Returns:
        GenresService:
    """
    return GenresService(
        db=GenresDataProvider(
            es_client=elastic,
            es_index=settings.GENRES_ES_INDEX,
        ),
        cache=RedisCache(
            redis_client=redis,
            model_class=Genre,
            ttl=GENRE_CACHE_EXPIRE_IN_SECONDS,
        ),
    )
