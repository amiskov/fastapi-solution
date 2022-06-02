from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError


class DataProvider(ABC):
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def get_list(self, **params) -> list:
        pass

    @abstractmethod
    async def get_search_result(self, **params) -> list:
        pass


@dataclass
class ElasticDataProvider:
    es_client: AsyncElasticsearch
    es_index: str

    async def get_by_id(self, entity_id: str) -> Optional[dict]:
        """Загрузка сущности по id."""
        try:
            doc = await self.es_client.get(self.es_index, entity_id)
        except NotFoundError:
            return None
        return doc['_source']

    async def _get_list_from_elastic(self, body: dict) -> list:
        try:
            doc = await self.es_client.search(index=self.es_index, body=body)
        except NotFoundError:
            return []
        items = [hit['_source'] for hit in doc['hits']['hits']]
        return items


class FilmsDataProvider(ElasticDataProvider, DataProvider):
    async def get_search_result(
            self,
            query: str,
            page_size: int,
            page_number: int,
    ) -> list:
        """Возвращает список сущностей, соответствующий критериям поиска."""
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

    async def get_list(
            self,
            sort: str,
            page_size: int,
            page_number: int,
            genre_id: str,
    ) -> list:
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
