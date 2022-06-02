from db.data_providers.base import BaseDataProvider
from db.data_providers.elastic import ElasticDataProvider


class FilmsDataProvider(ElasticDataProvider, BaseDataProvider):

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

    async def get_search_result(self, **kwargs) -> list:
        """Возвращает список сущностей, соответствующий критериям поиска."""
        return await self._search_elastic(
            **kwargs,
            fields=['title^3', 'description'],
        )
