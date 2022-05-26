"""API персон."""
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from models.person import PersonAPIResponse
from services.person import PersonsService, get_persons_service

router = APIRouter()


@router.get('/search', response_model=list[PersonAPIResponse])
async def persons_search(
        person_service: PersonsService = Depends(get_persons_service),
        query: str = None,
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
) -> list[PersonAPIResponse]:
    """Возвращает список персон для отправки по API, соответствующий критериям поиска."""
    if not query:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Query parameter is required.',
        )

    search_result = await person_service.get_search_result(
        query=query,
        page_size=page_size,
        page_number=page_number,
    )

    if not search_result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Persons not found.',
        )

    return [PersonAPIResponse(**item.dict()) for item in search_result]


@router.get('/', response_model=list[PersonAPIResponse])
async def persons_list(
        person_service: PersonsService = Depends(get_persons_service),
        sort: Optional[str] = '-id',
        page_size: int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1),
) -> list[PersonAPIResponse]:
    """Возвращает список персон для отправки по API, соответствующий критериям фильтрации."""
    persons = await person_service.get_list(
        sort=sort,
        page_size=page_size,
        page_number=page_number,
    )

    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='persons not found',
        )

    return [PersonAPIResponse(**item.dict()) for item in persons]


@router.get('/{person_id}', response_model=PersonAPIResponse)
async def person_details(
        person_id: str,
        person_service: PersonsService = Depends(get_persons_service),
) -> PersonAPIResponse:
    """Детализация персоны.

    Args:
        person_id (str):
        person_service (PersonsService, optional):

    Returns:
        PersonAPIResponse:
    """
    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='person not found',
        )

    return PersonAPIResponse(**person.dict())
