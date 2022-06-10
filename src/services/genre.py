"""Сервис загрузки жанров."""
from dataclasses import dataclass
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from core.config import settings
from db.cache.base import AsyncCacheStorage
from db.cache.redis import Cache, get_redis
from db.data_providers.base import AsyncDataProvider
from db.data_providers.elastic import get_elastic
from db.data_providers.genres import GenresDataProvider
from models.genre import Genre
from services.base_service import BaseService

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


@dataclass
class GenresService(BaseService):
    """Сервис загрузки жанров."""

    db: GenresDataProvider
    cache: Cache


@lru_cache()
def get_genres_service(
        cache: AsyncCacheStorage = Depends(get_redis),
        db: AsyncDataProvider = Depends(get_elastic),
) -> GenresService:
    """
    Сервис по загрузке жанров.

    Args:
        cache:
        db:

    Returns:
        GenresService:
    """
    return GenresService(
        db=GenresDataProvider(
            db_client=db,
            db_index=settings.GENRES_ES_INDEX,
        ),
        cache=Cache(
            cache_client=cache,
            model_class=Genre,
            ttl=GENRE_CACHE_EXPIRE_IN_SECONDS,
        ),
    )
