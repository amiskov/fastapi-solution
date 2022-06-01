from abc import ABC, abstractmethod
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


class ElasticDataProvider(DataProvider):
    def __init__(self, elastic: AsyncElasticsearch, es_index: str) -> None:
        self.es_index = es_index
        self.elastic = elastic

    async def get_by_id(self, entity_id: str) -> Optional[dict]:
        """Загрузка сущности по id."""
        try:
            doc = await self.elastic.get(self.es_index, entity_id)
        except NotFoundError:
            return None
        return doc['_source']

    async def get_search_result(
            self,
            search_query: dict,
            page_size: int,
            page_number: int,
    ) -> list:
        """Возвращает список сущностей, соответствующий критериям поиска."""
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': search_query,
        }
        return await self._get_list_from_elastic(body)

    async def get_list(
            self,
            sort: dict,
            page_size: int,
            page_number: int,
            query: dict,
    ) -> list:
        """Возвращает список сущностей с опциональной фильтрацией по ID жанра."""
        body = {
            'sort': sort,
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': query,
        }
        return await self._get_list_from_elastic(body)

    async def _get_list_from_elastic(self, body: dict) -> list:
        try:
            doc = await self.elastic.search(index=self.es_index, body=body)
        except NotFoundError:
            return []
        items = [hit['_source'] for hit in doc['hits']['hits']]
        return items
