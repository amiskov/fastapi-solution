"""Abstract caching class."""
from abc import ABC, abstractmethod
from typing import Callable, Optional, Union

from pydantic import BaseModel


class AsyncCacheStorage(ABC):
    """Abstract Caching Storage."""

    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value: bytes, expire: int, **kwargs):
        pass


class BaseCache(ABC):
    """Base abstraction for a cache."""

    @abstractmethod
    async def get_from_cache_or_db(
            self,
            get_from_db: Callable,
            **kwargs,
    ) -> Union[Optional[BaseModel], list[BaseModel]]:
        """
        Возвращает сущность или список сущностей из кэша.

        Если данных в кэше нет, ходит за ними в источник данных с помощью
        `get_from_db` и именованных аргументов `kwargs`.
        """
