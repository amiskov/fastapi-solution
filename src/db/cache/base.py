from abc import ABC, abstractmethod
from typing import Callable, Optional

from pydantic import BaseModel


class BaseCache(ABC):
    @abstractmethod
    async def get_entity_from_cache_or_db(
            self,
            get_entity_from_db_fn: Callable,
            entity_id: str
    ) -> Optional[BaseModel]:
        """Возвращает сущность из кэша. Если её в кэше нет, ходит за ней
        в источник данных с помощью `get_entity_from_db_fn` и `entity_id`."""

    @abstractmethod
    async def get_list_from_cache_or_db(
            self,
            get_list_from_db_fn: Callable,
            **kwargs
    ) -> list[BaseModel]:
        """Возвращает список сущностей из кэша. Если их в кэше нет, ходит за
        ними в источник данных с помощью `get_list_from_db_fn` и именованных
        аргументов `kwargs`."""
