"""Утилиты для наполнения тестовыми данными."""

import json
from asyncio import sleep
from typing import Any

import orjson


def generate_es_bulk_data(data: list[dict], index: str) -> str:
    """Генерация данных для множественного запроса в ElasticSearch."""
    save_list = []
    for item in data:
        save_list.append(json.dumps({'index': {'_index': index, '_id': item.get('id')}}))
        save_list.append(json.dumps(item))

    return '\n'.join(save_list) + '\n'


async def fake_cache(redis_client, key: str, value: Any) -> None:
    """Наполнение кеша редис данными."""
    await redis_client.set(
        key=key,
        value=orjson.dumps(value),
    )


async def fake_es(es_client, index: str, data: str) -> None:
    """Наполнение кеша редис данными."""
    await es_client.bulk(
        body=data,
        index=index,
    )

    # ElasticSearch принимает изменения не моментально!
    # TODO: подумать, как это обойти или проверить. waiter(?)
    await sleep(1)
