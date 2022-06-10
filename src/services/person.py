"""Сервис загрузки персон."""
from dataclasses import dataclass
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from core.config import settings
from db.cache.base import AsyncCacheStorage
from db.cache.redis import Cache, get_redis
from db.data_providers.elastic import get_elastic
from db.data_providers.persons import PersonsDataProvider
from models.person import Person
from services.base_service import BaseService

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


@dataclass
class PersonsService(BaseService):
    """Serves the Person model."""

    db: PersonsDataProvider
    cache: Cache


@lru_cache()
def get_persons_service(
        cache: AsyncCacheStorage = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonsService:
    """
    Сервис по загрузке персон.

    Args:
        cache:
        elastic:

    Returns:
        PersonsService:
    """
    return PersonsService(
        db=PersonsDataProvider(
            es_client=elastic,
            es_index=settings.PERSONS_ES_INDEX,
        ),
        cache=Cache(
            cache_client=cache,
            model_class=Person,
            ttl=PERSON_CACHE_EXPIRE_IN_SECONDS,
        ),
    )
