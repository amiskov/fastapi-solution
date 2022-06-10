"""Base abstraction for data providers."""
from abc import ABC, abstractmethod
from typing import Optional


class AsyncDataProvider(ABC):
    """Abstract Data Provider."""

    @abstractmethod
    async def get(self, index: str, entity_id: str) -> Optional[dict]:
        """Get the entity by id."""

    @abstractmethod
    async def search(self, **kwargs) -> list:
        """Get entities according the `kwargs` criteria."""


class BaseDataProvider(ABC):
    """Base abstraction for data providers."""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[dict]:
        """Get the entity by id."""

    @abstractmethod
    async def get_list(self, **kwargs) -> list:
        """Get entities according the `kwargs` criteria."""

    @abstractmethod
    async def get_search_result(self, **kwargs) -> list:
        """Find the entities according the `kwargs` criteria."""
