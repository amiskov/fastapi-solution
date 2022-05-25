"""Сервис загрузки жанров."""
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenresService:
    """Сервис GenresService."""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        self.redis = redis
        self.elastic = elastic

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
                index='genres',
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

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        """
        Загрузка данных по id.

        Args:
            genre_id:

        Returns:
            Genre (optional):
        """
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        """
        Загрузка жанра из ElasticSearch.

        Args:
            genre_id:

        Returns:
            Genre (optional):
        """
        try:
            doc = await self.elastic.get('genres', genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        """
        Загрузка жанра из кэша (redis).

        Args:
            genre_id:

        Returns:
            Genre (optional):
        """
        data = await self.redis.get(genre_id)
        if not data:
            return None

        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre) -> None:
        """
        Загрузка жанра в кэш (redis).

        Args:
            genre:

        Returns:
            None.
        """
        await self.redis.set(genre.id, genre.json(),
                             expire=FILM_CACHE_EXPIRE_IN_SECONDS)

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
                index='genres',
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
