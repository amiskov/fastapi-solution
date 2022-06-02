"""Сервис загрузки кинопроизведений."""
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.cache import Cache, CacheWithRedis
from db.data import DataProvider, FilmsElasticDataProvider
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    """Сервис FilmService."""

    def __init__(
            self,
            data_provider: DataProvider,
            cache_provider: Cache,
    ) -> None:
        self.db = data_provider
        self.cache = cache_provider

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Загрузка кинопроизведения по id."""
        res = await self.cache.get_entity_from_cache_or_db(
            get_entity_from_db_fn=self.db.get_by_id,
            entity_id=film_id
        )
        return res

    async def get_list(
            self,
            **kwargs
    ) -> list[Film]:
        films = await self.cache.get_list_from_cache_or_db(
            get_list_from_db_fn=self.db.get_list,
            **kwargs,
        )
        return films

    async def get_search_result(
            self,
            query: str,
            page_size: int,
            page_number: int,
    ) -> list[Film]:
        """Возвращает список фильмов, соответствующий критериям поиска."""
        search_query = {
            'multi_match': {
                'query': query,
                'fields': ['title^3', 'description'],
                'operator': 'and',
                'fuzziness': 'AUTO',
            },
        }
        found_films = await self.db.get_search_result(
            page_size=page_size,
            page_number=page_number,
            search_query=search_query,
        )
        return [Film(**item) for item in found_films]


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
        data_provider=FilmsElasticDataProvider(elastic=elastic, es_index='movies'),
        cache_provider=CacheWithRedis(redis=redis, caching_model_class=Film)
    )
