"""Конфигурации сервиса."""
import os
from logging import config as logging_config

from pydantic import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    """Project settings."""

    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'movies')

    REDIS_HOST: str = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))

    ELASTIC_HOST: str = os.getenv('ELASTIC_HOST', '127.0.0.1')
    ELASTIC_PORT: int = int(os.getenv('ELASTIC_PORT', 9200))

    MOVIES_ES_INDEX: str = os.getenv('MOVIES_ES_INDEX', 'movies')
    PERSONS_ES_INDEX: str = os.getenv('PERSONS_ES_INDEX', 'persons')
    GENRES_ES_INDEX: str = os.getenv('GENRES_ES_INDEX', 'genres')

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Config:
        """Env variables filename."""

        env_file = '.env'


settings = Settings()
