"""Сервис загрузки персон."""
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonsService:
    """Сервис PersonsService."""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch) -> None:
        self.redis = redis
        self.elastic = elastic

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
            doc = await self.elastic.search(
                index='persons',
                body={
                    'sort': {sort_term: {'order': order}},
                    'size': page_size,
                    'from': (page_number - 1) * page_size,
                    'query': query,
                },
            )
        except NotFoundError:
            return []

        persons = [Person(**hit['_source']) for hit in doc['hits']['hits']]
        return persons

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        """
        Загрузка данных по id.

        Args:
            person_id:

        Returns:
            Person (optional):
        """
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        """
        Загрузка персоны из ElasticSearch.

        Args:
            person_id:

        Returns:
            Person (optional):
        """
        try:
            doc = await self.elastic.get('persons', person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        """
        Загрузка персоны из кэша (redis).

        Args:
            person_id:

        Returns:
            Person (optional):
        """
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person) -> None:
        """
        Загрузка персоны в кэш (redis).

        Args:
            person:

        Returns:
            None.
        """
        await self.redis.set(person.id, person.json(),
                             expire=FILM_CACHE_EXPIRE_IN_SECONDS)

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
                index='persons',
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
