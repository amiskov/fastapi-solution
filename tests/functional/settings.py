"""Конфигурации для тестов."""
from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    """Конфигурации для тестов."""

    service_url: str = Field('http://127.0.0.1:8002', env='SERVICE_URL')
    PERSONS_ES_INDEX: str = Field('persons', env='PERSONS_ES_INDEX')
    GENRES_ES_INDEX: str = Field('genres', env='GENRES_ES_INDEX')
    MOVIES_INDEX: str = Field('movies', env='MOVIES_INDEX')
    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: str = Field('6379', env='REDIS_PORT')
    redis_url: str = Field('http://127.0.0.1:6379', env='REDIS_URL')
    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')


settings = TestSettings()
