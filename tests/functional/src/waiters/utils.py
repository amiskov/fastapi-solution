import logging
from functools import wraps
from time import sleep
from typing import Any, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Waiter")
MAX_RETRY_NUMBER = 10


def _get_sleep_time(step: int, start_sleep_time: float, factor: int, border_sleep_time: float) -> float:
    sleep_time = start_sleep_time * (factor**step)
    return sleep_time if sleep_time < border_sleep_time else border_sleep_time


def _on_exception(
        exception: Exception,
        service: str,
        step: int,
        sleep_time: float,
        start_sleep_time: float = 0.1,
        factor: int = 2,
        border_sleep_time: int = 10,
) -> float:
    if sleep_time < border_sleep_time:
        sleep_time = _get_sleep_time(
            step, start_sleep_time, factor, border_sleep_time,
        )
    logger.warning(
        f'Error connecting {service}. '
        f'Exception: {exception}. '
        f'Trying again in {sleep_time} seconds...'
    )
    sleep(sleep_time)
    return sleep_time


def backoff(service: str, start_sleep_time: float = 0.1, factor: int = 2, border_sleep_time: int = 10) -> Callable:
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.

    Использует наивный экспоненциальный рост времени повтора (factor)
    до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    """

    def func_wrapper(func: Callable) -> Callable:
        @wraps(func)
        async def inner(*args, **kwargs) -> Any:
            sleep_time = 0
            for step in range(MAX_RETRY_NUMBER):
                try:
                    await func(*args, **kwargs)
                    exit(0)
                except Exception as exception:
                    sleep_time = _on_exception(
                        service=service, exception=exception, step=step, sleep_time=sleep_time,
                        start_sleep_time=start_sleep_time, factor=factor, border_sleep_time=border_sleep_time,
                    )

            logger.exception(
                f"The maximum retry number ({MAX_RETRY_NUMBER}) has been reached. "
                f"Service {service} is not ready."
            )
            exit(1)

        return inner

    return func_wrapper
