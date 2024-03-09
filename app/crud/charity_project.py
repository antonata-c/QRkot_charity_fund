from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject
from app.schemas.charity_project import CharityProjectCreate


class CRUDCharityProject(
    CRUDBase[
        CharityProject,
        CharityProjectCreate
    ]
):
    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> list[CharityProject]:
        charity_projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested == 1
            ).order_by(CharityProject.close_date - CharityProject.create_date)
        )
        return charity_projects.scalars().all()


charity_project_crud = CRUDCharityProject(CharityProject)
