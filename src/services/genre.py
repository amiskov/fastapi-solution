"""Сервис загрузки жанров."""
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import cache_details, cache_list, get_redis
from models.genre import Genre

from core.config import settings

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenresService:
    """Сервис GenresService."""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        self.redis = redis
        self.elastic = elastic

    @cache_list(Genre, ttl=GENRE_CACHE_EXPIRE_IN_SECONDS)
    async def get_list(
            self,
            sort: str,
            page_size: int,
            page_number: int,
    ) -> list[Genre]:
        """
        Возвращает список жанров..
        """
        is_desc_sorting = sort.startswith('-')
        order = 'desc' if is_desc_sorting else 'asc'
        sort_term = sort[1:] if is_desc_sorting else sort
        query = {'match_all': {}}

        try:
            doc = await self.elastic.search(
                index=settings.GENRES_ES_INDEX,
                body={
                    'sort': {sort_term: {'order': order}},
                    'size': page_size,
                    'from': (page_number - 1) * page_size,
                    'query': query,
                },
            )
        except NotFoundError:
            return []

        genres = [Genre(**hit['_source']) for hit in doc['hits']['hits']]
        return genres

    @cache_details(Genre, ttl=GENRE_CACHE_EXPIRE_IN_SECONDS)
    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        """
        Загрузка данных по id.

        Args:
            genre_id:

        Returns:
            Genre (optional):
        """
        try:
            doc = await self.elastic.get(settings.GENRES_ES_INDEX, genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    @cache_list(Genre, ttl=GENRE_CACHE_EXPIRE_IN_SECONDS)
    async def get_search_result(
            self,
            query: str,
            page_size: int,
            page_number: int,
    ) -> list[Genre]:
        """Возвращает список жанров, соответствующий критериям поиска."""
        search_query = {
            'multi_match': {
                'query': query,
                'fields': ['name', 'description'],
                'operator': 'and',
                'fuzziness': 'AUTO',
            },
        }
        try:
            doc = await self.elastic.search(
                index=settings.GENRES_ES_INDEX,
                body={
                    'size': page_size,
                    'from': (page_number - 1) * page_size,
                    'query': search_query,
                },
            )
        except NotFoundError:
            return []

        genres = [Genre(**hit['_source']) for hit in doc['hits']['hits']]
        return genres


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
    return GenresService(redis, elastic)
