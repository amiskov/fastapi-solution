"""Сервис загрузки кинопроизведений."""
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.data import DataProvider, ElasticDataProvider
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    """Сервис FilmService."""

    def __init__(self, data_provider: DataProvider) -> None:
        self.db = data_provider

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Загрузка кинопроизведения по id."""
        res = await self.db.get_by_id(film_id)
        if not res:
            return None
        return Film(**res)

    async def get_list(
            self,
            sort: str,
            page_size: int,
            page_number: int,
            genre_id: str,
    ) -> list[Film]:
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
        films = await self.db.get_list(
            sort={sort_term: {'order': order}},
            page_size=page_size,
            page_number=page_number,
            query=query
        )
        return [Film(**item) for item in films]

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
        data_provider=ElasticDataProvider(elastic=elastic, es_index='movies')
    )
