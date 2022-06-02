"""Сервис загрузки персон."""
from dataclasses import dataclass
from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.cache.redis import RedisCache, get_redis
from db.data_providers.elastic import get_elastic
from db.data_providers.persons import PersonsDataProvider
from models.person import Person
from services.base_service import BaseService

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


@dataclass
class PersonsService(BaseService):
    db: PersonsDataProvider
    cache: RedisCache


@lru_cache()
def get_persons_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonsService:
    """
    Сервис по загрузке персон.

    Args:
        redis:
        elastic:

    Returns:
        PersonsService:
    """
    return PersonsService(
        db=PersonsDataProvider(es_client=elastic, es_index='persons'),
        cache=RedisCache(
            redis_client=redis,
            model_class=Person,
            ttl=PERSON_CACHE_EXPIRE_IN_SECONDS
        )
    )
