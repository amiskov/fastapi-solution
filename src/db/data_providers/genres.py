from db.data_providers.base import BaseDataProvider
from db.data_providers.elastic import ElasticDataProvider


class GenresDataProvider(ElasticDataProvider, BaseDataProvider):
    async def get_list(
            self,
            sort: str,
            page_size: int,
            page_number: int,
    ) -> list:
        """
        Возвращает список жанров..
        """
        is_desc_sorting = sort.startswith('-')
        order = 'desc' if is_desc_sorting else 'asc'
        sort_term = sort[1:] if is_desc_sorting else sort
        query = {'match_all': {}}
        body = {
            'sort': {sort_term: {'order': order}},
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': query,
        }
        return await self._get_list_from_elastic(body)

    async def get_search_result(self, **kwargs) -> list:
        """Возвращает список сущностей, соответствующий критериям поиска."""
        return await self._search_elastic(
            **kwargs,
            fields=['name', 'description']
        )
