"""Provides the data for a Person."""
from db.data_providers.elastic import ElasticDataProvider


class PersonsDataProvider(ElasticDataProvider):
    """Provides the data for a Person from Elastic."""

    async def get_search_result(self, **kwargs) -> list[dict]:
        """Ищет персон по заданным параметрам."""
        return await self._search_elastic(fields=['name'], **kwargs)
