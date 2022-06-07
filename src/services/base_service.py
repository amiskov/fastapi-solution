from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from db.data_providers.base import BaseDataProvider


@dataclass
class BaseService:
    db: BaseDataProvider

    async def get_by_id(self, entity_id: str) -> Optional[BaseModel]:
        """Загрузка сущности по id."""
        return await self.db.get_by_id(entity_id)

    async def get_list(self, **kwargs) -> list[BaseModel]:
        return await self.db.get_list(**kwargs)

    async def get_search_result(self, **kwargs) -> list[BaseModel]:
        """Возвращает список фильмов, соответствующий критериям поиска."""
        return await self.db.get_search_result(**kwargs)
