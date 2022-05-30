"""HTTP Exceptions."""
from http import HTTPStatus
from typing import Any, Optional

from fastapi import HTTPException


class FilmNotFoundException(HTTPException):
    """Film not found."""

    def __init__(self, headers: Optional[dict[str, Any]] = None) -> None:
        super(FilmNotFoundException, self).__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Film not found.',
            headers=headers,
        )


class GenreNotFoundException(HTTPException):
    """Genre not found."""

    def __init__(self, headers: Optional[dict[str, Any]] = None) -> None:
        super(GenreNotFoundException, self).__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Genre not found.',
            headers=headers,
        )


class PersonNotFoundException(HTTPException):
    """Person not found."""

    def __init__(self, headers: Optional[dict[str, Any]] = None) -> None:
        super(PersonNotFoundException, self).__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Person not found.',
            headers=headers,
        )


class MissedQueryParameterException(HTTPException):
    """Genre not found."""

    def __init__(self, parameter: str, headers: Optional[dict[str, Any]] = None) -> None:
        super(MissedQueryParameterException, self).__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'Query parameter is required: {parameter}.',
            headers=headers,
        )
