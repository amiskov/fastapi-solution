"""Конфигурации для тестов."""
from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    """Конфигурации для тестов."""

    SERVICE_URL: str = Field('http://127.0.0.1:8002', env='SERVICE_URL')
    PERSONS_ES_INDEX: str = Field('persons', env='PERSONS_ES_INDEX')
    GENRES_ES_INDEX: str = Field('genres', env='GENRES_ES_INDEX')
    MOVIES_INDEX: str = Field('movies', env='MOVIES_INDEX')
    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: str = Field('6379', env='REDIS_PORT')
    ELASTIC_URL: str = Field('http://127.0.0.1:9200', env='ELASTIC_URL')
    STATIC_ES_MOVIES_INDEX_PATH: str = Field('../static/create_movies_index.json', env='STATIC_ES_MOVIES_INDEX_PATH')
    STATIC_ES_PERSONS_INDEX_PATH: str = Field('../static/create_persons_index.json', env='STATIC_ES_PERSONS_INDEX_PATH')
    STATIC_ES_GENRES_INDEX_PATH: str = Field('../static/create_genres_index.json', env='STATIC_ES_GENRES_INDEX_PATH')


settings = TestSettings()
