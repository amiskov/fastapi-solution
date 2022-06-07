"""Provides the data for the Genre models."""
from db.data_providers.elastic import ElasticDataProvider


class GenresDataProvider(ElasticDataProvider):
    """Provides the data for the Genre models."""

    async def get_search_result(self, **kwargs) -> list[dict]:
        """Ищет жанры по заданным параметрам."""
        return await self._search_elastic(
            fields=['name', 'description'],
            **kwargs,
        )
