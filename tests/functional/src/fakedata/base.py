from tests.functional.src.fakedata.utils import fake_es, generate_es_bulk_data, fake_cache


def get_cache_key(
        data_key: str,
        page_size: int = 50,
        page_number: int = 1,
) -> str:
    return f'{data_key}:get_list:sort=-id:page_size={page_size}:page_number={page_number}'


async def fake_es_index(
        es_client,
        index: str,
        data: list[dict],
        limit: int = 50,
) -> list[dict]:
    """Наполнение данными индекс persons."""
    result_data = data[:limit]
    await fake_es(
        es_client=es_client,
        index=index,
        data=generate_es_bulk_data(
            data=result_data,
            index=index,
        ),
    )
    return result_data


async def fake_cache_list_data(
        redis_client,
        data: list[dict],
        data_key: str,
        page_size: int = 50,
        page_number: int = 1,
        limit: int = 50,
) -> list[dict]:
    """Наполнение кеша редис данными."""
    offset = page_size * (page_number - 1)
    result_data = data[offset:offset+limit]
    await fake_cache(
        redis_client=redis_client,
        key=get_cache_key(data_key=data_key, page_size=page_size, page_number=page_number),
        value=result_data,
    )
    return result_data