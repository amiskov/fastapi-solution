"""Сервис загрузки персон."""
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from core.config import settings
from db.elastic import get_elastic
from db.redis import cache_details, cache_list, get_redis
from models.person import Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonsService:
    """Сервис PersonsService."""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        self.redis = redis
        self.elastic = elastic

    @cache_list(Person, ttl=PERSON_CACHE_EXPIRE_IN_SECONDS)
    async def get_list(
            self,
            sort: str,
            page_size: int,
            page_number: int,
    ) -> list[Person]:
        """
        Возвращает список персон..
        """
        is_desc_sorting = sort.startswith('-')
        order = 'desc' if is_desc_sorting else 'asc'
        sort_term = sort[1:] if is_desc_sorting else sort
        query = {'match_all': {}}

        try:
            body = {
                'sort': {sort_term: {'order': order}},
                'size': page_size,
                'from': (page_number - 1) * page_size,
                'query': query,
            }

            doc = await self.elastic.search(
                index=settings.PERSONS_ES_INDEX,
                body=body,
            )

        except NotFoundError:
            return []

        persons = [Person(**hit['_source']) for hit in doc['hits']['hits']]
        return persons

    @cache_details(Person, ttl=PERSON_CACHE_EXPIRE_IN_SECONDS)
    async def get_by_id(self, person_id: str) -> Optional[Person]:
        """
        Загрузка данных по id.

        Args:
            person_id:

        Returns:
            Person (optional):
        """
        try:
            doc = await self.elastic.get(settings.PERSONS_ES_INDEX, person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    @cache_list(Person, ttl=PERSON_CACHE_EXPIRE_IN_SECONDS)
    async def get_search_result(
            self,
            query: str,
            page_size: int,
            page_number: int,
    ) -> list[Person]:
        """Возвращает список персон, соответствующий критериям поиска."""
        search_query = {
            'multi_match': {
                'query': query,
                'fields': ['name'],
                'operator': 'and',
                'fuzziness': 'AUTO',
            },
        }
        try:
            doc = await self.elastic.search(
                index=settings.PERSONS_ES_INDEX,
                body={
                    'size': page_size,
                    'from': (page_number - 1) * page_size,
                    'query': search_query,
                },
            )
        except NotFoundError:
            return []

        persons = [Person(**hit['_source']) for hit in doc['hits']['hits']]
        return persons


@lru_cache()
def get_persons_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonsService:
    """
    Сервис по загрузке персон.

    Args:
        redis:
        elastic:

    Returns:
        PersonsService:
    """
    return PersonsService(redis, elastic)
