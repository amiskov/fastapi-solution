"""Сервис загрузки кинопроизведений."""
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    """Сервис FilmService (TODO)."""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        self.redis = redis
        self.elastic = elastic

    async def get_list(self,
                       sort: str,
                       page_size: int,
                       page_number: int,
                       genre_id: str) -> list[Film]:
        """Возвращает список фильмов, который может быть отфильтрован
        по ID жанра."""
        is_desc_sorting = sort.startswith('-')
        order = 'desc' if is_desc_sorting else 'asc'
        sort_term = sort[1:] if is_desc_sorting else sort

        if genre_id:
            query = {
                "bool": {
                    "filter": [{
                        "nested": {
                            "path": "genre",
                            "query": {
                                "bool": {
                                    "filter": [{
                                        "term": {
                                            "genre.id": genre_id
                                        }
                                    }]
                                }
                            }
                        }
                    }]
                }
            }
        else:
            query = {'match_all': {}}

        try:
            doc = await self.elastic.search(
                index='movies',
                body={
                    'sort': {sort_term: {'order': order}},
                    'size': page_size,
                    'from': (page_number - 1) * page_size,
                    'query': query})
        except NotFoundError:
            return []

        films = [Film(**hit['_source']) for hit in doc['hits']['hits']]
        return films

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """
        Загрузка данных по id.

        Args:
            film_id:

        Returns:
            Film (optional):
        """
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        """
        Загрузка кинопроизведения из ElasticSearch.

        Args:
            film_id:

        Returns:
            Film (optional):
        """
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        """
        Загрузка кинопроизведения из кэша (redis).

        Args:
            film_id:

        Returns:
            Film (optional):
        """
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film) -> None:
        """
        Загрузка фильма в кэш (redis).

        Args:
            film:

        Returns:
            None.
        """
        await self.redis.set(film.id, film.json(),
                             expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_search_result(self,
                                query: str,
                                page_size: int,
                                page_number: int) -> list[Film]:
        """Возвращает список фильмов, соответствующий критериям поиска."""
        search_query = {
            'multi_match': {
                'query': query,
                'fields': ['title^3', 'description'],
                'operator': 'and',
                'fuzziness': 'AUTO',
            },
        }
        try:
            doc = await self.elastic.search(
                index='movies',
                body={
                    'size': page_size,
                    'from': (page_number - 1) * page_size,
                    'query': search_query,
                })
        except NotFoundError:
            return []

        films = [Film(**hit['_source']) for hit in doc['hits']['hits']]
        return films


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
