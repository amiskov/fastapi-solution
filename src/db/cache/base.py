from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class BaseCache(ABC):
    @abstractmethod
    async def get_entity_from_cache_or_db(
            self,
            **kwargs
    ) -> Optional[BaseModel]:
        pass

    @abstractmethod
    async def get_list_from_cache_or_db(self, **kwargs) -> list[BaseModel]:
        pass
