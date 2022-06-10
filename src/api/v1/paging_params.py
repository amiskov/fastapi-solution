"""Common paging params for API queries."""
from dataclasses import dataclass

from fastapi import Query


@dataclass
class PagingParams:
    """Common paging params for API queries."""

    page_number: int = Query(default=1, alias='page[number]')
    page_size: int = Query(default=50, alias='page[size]')
