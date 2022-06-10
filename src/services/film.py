"""Сервис загрузки кинопроизведений."""
from dataclasses import dataclass
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from core.config import settings
from db.cache.base import AsyncCacheStorage
from db.cache.redis import Cache, get_redis
from db.data_providers.base import AsyncDataProvider
from db.data_providers.elastic import get_elastic
from db.data_providers.films import FilmsDataProvider
from models.film import Film
from services.base_service import BaseService

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


@dataclass
class FilmService(BaseService):
    """Serves the Film model."""

    db: FilmsDataProvider
    cache: Cache


@lru_cache()
def get_film_service(
        cache: AsyncCacheStorage = Depends(get_redis),
        db: AsyncDataProvider = Depends(get_elastic),
) -> FilmService:
    """
    Сервис по загрузке кинопроизведений.

    Args:
        cache:
        db:

    Returns:
        FilmService:
    """
    return FilmService(
        db=FilmsDataProvider(
            db_client=db,
            db_index=settings.MOVIES_ES_INDEX,
        ),
        cache=Cache(
            cache_client=cache,
            model_class=Film,
            ttl=FILM_CACHE_EXPIRE_IN_SECONDS,
        ),
    )
