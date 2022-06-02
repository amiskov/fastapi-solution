from db.data_providers.base import BaseDataProvider
from db.data_providers.elastic import ElasticDataProvider


class FilmsDataProvider(ElasticDataProvider, BaseDataProvider):
    async def get_list(self, genre_id: str, **kwargs) -> list:
        """Возвращает список фильмов с опциональной фильтрацией по ID жанра."""
        query = None
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
        return await self._get_list_from_elastic(query=query, **kwargs)

    async def get_search_result(self, **kwargs) -> list:
        """Возвращает список сущностей, соответствующий критериям поиска."""
        return await self._search_elastic(
            fields=['title^3', 'description'],
            **kwargs,
        )
