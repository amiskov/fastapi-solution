from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from db.cache.base import BaseCache
from db.data_providers.base import BaseDataProvider


@dataclass
class BaseService:
    db: BaseDataProvider
    cache: BaseCache

    async def get_by_id(self, entity_id: str) -> Optional[BaseModel]:
        """Загрузка сущности по id."""
        return await self.cache.get_entity_from_cache_or_db(
            get_entity_from_db_fn=self.db.get_by_id,
            entity_id=entity_id
        )

    async def get_list(self, **kwargs) -> list[BaseModel]:
        return await self.cache.get_list_from_cache_or_db(
            get_list_from_db_fn=self.db.get_list,
            **kwargs,
        )

    async def get_search_result(self, **kwargs) -> list[BaseModel]:
        """Возвращает список фильмов, соответствующий критериям поиска."""
        return await self.cache.get_list_from_cache_or_db(
            get_list_from_db_fn=self.db.get_search_result,
            **kwargs,
        )
