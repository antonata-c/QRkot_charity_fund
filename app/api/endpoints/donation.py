from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB, DonationUserDB
from app.services.investments import make_investment

router = APIRouter()


@router.get(
    '/',
    response_model_exclude_none=True,
    response_model=list[DonationDB]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Для суперюзеров.
    Возвращает все пожертвования
    """
    donations = await donation_crud.get_multi(session)
    return donations


@router.post(
    '/',
    response_model_exclude_none=True,
    response_model=DonationUserDB
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """
    Только для авторизованного пользователя.
    Создает новое пожертвование
    """
    new_donation = await donation_crud.create(
        obj_in=donation,
        session=session,
        user=user,
        commit=False
    )

    session.add_all(
        make_investment(
            new_donation, await charity_project_crud.get_not_fully_invested(
                session
            )
        )
    )
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/my',
    response_model_exclude_none=True,
    response_model=list[DonationUserDB]
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """
    Только для авторизованных пользователей.
    Возвращает список пожертвований пользователя, выполнившего запрос
    """
    donations = await donation_crud.get_by_user(
        session, user
    )
    return donations
