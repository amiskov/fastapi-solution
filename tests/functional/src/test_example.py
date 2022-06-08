import pytest
from functional.settings import settings

SERVICE_URL = settings.service_url


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
