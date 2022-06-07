"""Загрузка ElasticSearch."""
from dataclasses import dataclass
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError

from db.data_providers.base import BaseDataProvider

es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> AsyncElasticsearch:
    """Загрузка ElasticSearch."""
    return es


@dataclass
class ElasticDataProvider(BaseDataProvider):
    """Provides the data from Elastic for models."""

    es_client: AsyncElasticsearch
    es_index: str

    async def get_by_id(self, entity_id: str) -> Optional[dict]:
        """Загрузка сущности по id."""
        try:
            doc = await self.es_client.get(self.es_index, entity_id)
        except NotFoundError:
            return None
        return doc['_source']

    async def get_list(self, **kwargs) -> list[dict]:
        """Возвращает список сущностей без фильтрации с параметрами."""
        return await self._get_list_from_elastic(
            query={'match_all': {}},
            **kwargs,
        )

    async def get_search_result(self, **kwargs) -> list:
        """Поиск 'по умолчанию': вернёт результат поиска по всем полям."""
        return await self._search_elastic(fields=['*'], **kwargs)

    async def _get_list_from_elastic(
            self,
            page_size: int,
            page_number: int,
            query: dict,
            sort: Optional[str] = None,
    ) -> list[dict]:
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': query,
        }
        if sort:
            is_desc_sorting = sort.startswith('-')
            order = 'desc' if is_desc_sorting else 'asc'
            sort_term = sort[1:] if is_desc_sorting else sort
            body['sort'] = {sort_term: {'order': order}}
        try:
            doc = await self.es_client.search(index=self.es_index, body=body)
        except NotFoundError:
            return []
        items = [hit['_source'] for hit in doc['hits']['hits']]
        return items

    async def _search_elastic(
            self,
            query: str,
            fields: list[str],
            **kwargs,
    ) -> list[dict]:
        search_query = {
            'multi_match': {
                'query': query,
                'fields': fields,
                'operator': 'and',
                'fuzziness': 'AUTO',
            },
        }
        return await self._get_list_from_elastic(
            query=search_query,
            **kwargs,
        )
