"""Описание ошибок для тестов."""


class ESResourceAlreadyExistsError(Exception):
    """При создании индекса произошла ошибка: такой индекс уже существует."""


class ESCreateIndexError(Exception):
    """При создании индекса произошла ошибка."""


class ESRemoveIndexError(Exception):
    """При удалении индекса произошла ошибка."""
