"""Base abstraction for a service."""
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from db.cache.base import BaseCache
from db.data_providers.base import BaseDataProvider


@dataclass
class BaseService:
    """Service functionality 'by default'."""

    db: BaseDataProvider
    cache: BaseCache

    async def get_by_id(self, film_id: str) -> Optional[BaseModel]:
        """Загрузка сущности по id."""
        return await self.cache.get_from_cache_or_db(
            get_from_db=self.db.get_by_id,
            entity_id=film_id,
        )

    async def get_list(self, **kwargs) -> list[BaseModel]:
        """Загрузка списка сущностей по заданным параметрам."""
        return await self.cache.get_from_cache_or_db(
            get_from_db=self.db.get_list,
            **kwargs,
        )

    async def get_search_result(self, **kwargs) -> list[BaseModel]:
        """Возвращает список фильмов, соответствующий критериям поиска."""
        return await self.cache.get_from_cache_or_db(
            get_from_db=self.db.get_search_result,
            **kwargs,
        )
