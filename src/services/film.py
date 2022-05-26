"""Сервис загрузки кинопроизведений."""
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import cache_details, cache_list, get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    """Сервис FilmService."""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        self.redis = redis
        self.elastic = elastic

    @cache_details(Film, ttl=FILM_CACHE_EXPIRE_IN_SECONDS)
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Загрузка кинопроизведения по id."""
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    @cache_list(Film, ttl=FILM_CACHE_EXPIRE_IN_SECONDS)
    async def get_list(
            self,
            sort: str,
            page_size: int,
            page_number: int,
            genre_id: str,
    ) -> list[Film]:
        """Возвращает список фильмов с опциональной фильтрацией по ID жанра."""
        is_desc_sorting = sort.startswith('-')
        order = 'desc' if is_desc_sorting else 'asc'
        sort_term = sort[1:] if is_desc_sorting else sort

        if genre_id:
            genre_nested_query = {
                'path': 'genre',
                'query': {
                    'bool': {
                        'filter': [{
                            'term': {
                                'genre.id': genre_id,
                            },
                        }],
                    },
                },
            }
            query = {
                'bool': {
                    'filter': [{
                        'nested': genre_nested_query,
                    }],
                },
            }
        else:
            query = {'match_all': {}}

        body = {
            'sort': {sort_term: {'order': order}},
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': query,
        }

        return await self._get_list_from_elastic(body)

    async def _get_list_from_elastic(self, body: dict) -> list[Film]:
        try:
            doc = await self.elastic.search(index='movies', body=body)
        except NotFoundError:
            return []

        films = [Film(**hit['_source']) for hit in doc['hits']['hits']]
        return films

    @cache_list(Film, ttl=FILM_CACHE_EXPIRE_IN_SECONDS)
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
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': search_query,
        }
        return await self._get_list_from_elastic(body)


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
    return FilmService(redis, elastic)
