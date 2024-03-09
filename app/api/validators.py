from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject

ALREADY_EXISTS = 'Проект с таким названием уже существует'
PROJECT_DOES_NOT_EXISTS = 'Указанный проект не существует'
PROJECT_ALREADY_CLOSED = 'Указанный проект закрыт'
INCORRECT_NEW_AMOUNT = 'Полная сумма не может быть меньше вложенной'
PROJECT_ALREADY_INVESTED = 'Удалять можно только проекты без инвестиций'


async def check_name_unique(
    charity_project_name: str,
    session: AsyncSession
):
    if await charity_project_crud.get_by_attribute(
        'name', charity_project_name, session
    ) is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ALREADY_EXISTS
        )


async def check_charity_project_exists(
    charity_project_id: int,
    session: AsyncSession
) -> CharityProject:
    charity_project = await charity_project_crud.get(
        charity_project_id, session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_DOES_NOT_EXISTS
        )
    return charity_project


def check_charity_project_open(
    charity_project: CharityProject
):
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_ALREADY_CLOSED
        )


def check_full_amount(
    already_invested_amount: int,
    new_amount: int,
):
    if new_amount < already_invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=INCORRECT_NEW_AMOUNT
        )


def check_project_not_invested(
    charity_project: CharityProject
):
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=PROJECT_ALREADY_INVESTED
        )
