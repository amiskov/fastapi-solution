from dataclasses import dataclass
from pprint import pprint
from typing import Optional

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

SERVICE_URL = 'http://127.0.0.1:8000'


@pytest.mark.asyncio
async def test_search_detailed(es_client, make_get_request):
    # Заполнение данных для теста
    # await es_client.bulk(...)

    # Выполнение запроса
    response = await make_get_request(
        '/films/search',
        {
            'query': 'Star Wars',
            'page[size]': 1,
        }
    )

    # Проверка результата
    assert response.status == 200
    assert len(response.body) == 1
    # вернётся список найденных фильмов, expected
    # assert response.body == expected
