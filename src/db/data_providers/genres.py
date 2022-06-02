from db.data_providers.elastic import ElasticDataProvider


class GenresDataProvider(ElasticDataProvider):
    async def get_search_result(self, **kwargs) -> list[dict]:
        """Возвращает список жанров, соответствующий критериям поиска
        по полям `fields`."""
        return await self._search_elastic(
            fields=['name', 'description'],
            **kwargs
        )
