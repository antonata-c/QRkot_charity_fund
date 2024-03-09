from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_charity_project_exists,
                                check_charity_project_open, check_full_amount,
                                check_name_unique, check_project_not_invested)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investments import make_investment

router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_projects(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Для всех пользователей.
    Возвращает список всех проектов
    """
    charity_projects = await charity_project_crud.get_multi(session)
    return charity_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=(Depends(current_superuser),)
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Для суперюзеров.
    Добавляет новый проект
    """
    await check_name_unique(charity_project.name, session)
    new_project = await charity_project_crud.create(
        obj_in=charity_project,
        session=session,
        commit=False
    )
    session.add_all(
        make_investment(
            new_project, await donation_crud.get_not_fully_invested(session)
        )
    )
    await session.commit()
    await session.refresh(new_project)
    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=(Depends(current_superuser),)
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Для суперюзеров.
    Обновляет информацию о проекте
    """
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    check_charity_project_open(charity_project)
    if obj_in.name:
        await check_name_unique(obj_in.name, session)
    if obj_in.full_amount:
        check_full_amount(
            charity_project.invested_amount,
            obj_in.full_amount,
        )
    charity_project = await charity_project_crud.update(
        charity_project,
        obj_in,
        session
    )
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=(Depends(current_superuser),)
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Для суперюзеров.
    Удаляет проект
    """
    charity_project = await check_charity_project_exists(project_id, session)
    check_project_not_invested(charity_project)
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project
