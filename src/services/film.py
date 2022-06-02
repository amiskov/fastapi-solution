"""Сервис загрузки кинопроизведений."""
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel

from db.cache import Cache, RedisCache
from db.data import DataProvider, FilmsDataProvider
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


@dataclass
class Service:
    db: DataProvider
    cache: Cache

    async def get_by_id(self, entity_id: str) -> Optional[BaseModel]:
        """Загрузка сущности по id."""
        return await self.cache.get_entity_from_cache_or_db(
            get_entity_from_db_fn=self.db.get_by_id,
            entity_id=entity_id
        )

    async def get_list(self, **kwargs) -> list[BaseModel]:
        return await self.cache.get_list_from_cache_or_db(
            get_list_from_db_fn=self.db.get_list,
            **kwargs,
        )

    async def get_search_result(self, **kwargs) -> list[BaseModel]:
        """Возвращает список фильмов, соответствующий критериям поиска."""
        return await self.cache.get_list_from_cache_or_db(
            get_list_from_db_fn=self.db.get_search_result,
            **kwargs,
        )


@dataclass
class FilmService(Service):
    db: FilmsDataProvider
    cache: RedisCache


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
        cache=RedisCache(redis=redis, caching_model_class=Film)
    )
