"""Загрузка ElasticSearch."""
from dataclasses import dataclass
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError

es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> AsyncElasticsearch:
    """Загрузка ElasticSearch."""
    return es


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

    async def _get_list_from_elastic(self, body: dict) -> list[dict]:
        try:
            doc = await self.es_client.search(index=self.es_index, body=body)
        except NotFoundError:
            return []
        items = [hit['_source'] for hit in doc['hits']['hits']]
        return items

    async def _search_elastic(
            self,
            query: str,
            page_size: int,
            page_number: int,
            fields: list[str]
    ) -> list[dict]:
        search_query = {
            'multi_match': {
                'query': query,
                'fields': fields,
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
