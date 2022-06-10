"""Provides the data for the Film models."""
from db.data_providers.elastic import ElasticDataProvider


class FilmsDataProvider(ElasticDataProvider):
    """Provides the data from Elastic for the Film models."""

    async def get_list(self, genre_id: str, **kwargs) -> list[dict]:
        """Возвращает список фильмов с опциональной фильтрацией по ID жанра."""
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
        return await self._get_list_from_elastic(query=query, **kwargs)

    async def get_search_result(self, **kwargs) -> list[dict]:
        """Возвращает список фильмов, соответствующий критериям поиска."""
        if 'fields' not in kwargs:
            kwargs['fields'] = ['title^3', 'description']
        return await self._search_elastic(**kwargs)
