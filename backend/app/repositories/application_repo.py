from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, ApplicationStatus
from app.schemas.application import ApplicationCreate, ApplicationUpdate


class ApplicationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, app_id: int) -> Optional[Application]:
        result = await self.db.execute(select(Application).where(Application.id == app_id))
        return result.scalar_one_or_none()

    async def get_by_user_and_program(
        self, user_id: int, program_id: int
    ) -> Optional[Application]:
        result = await self.db.execute(
            select(Application).where(
                Application.user_id == user_id,
                Application.program_id == program_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, data: ApplicationCreate) -> Application:
        application = Application(
            user_id=user_id,
            program_id=data.program_id,
            motivation_letter=data.motivation_letter,
            cv_url=data.cv_url,
        )
        self.db.add(application)
        await self.db.flush()
        await self.db.refresh(application)
        return application

    async def update(self, application: Application, data: ApplicationUpdate) -> Application:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(application, field, value)
        await self.db.flush()
        await self.db.refresh(application)
        return application

    async def delete(self, application: Application) -> None:
        await self.db.delete(application)
        await self.db.flush()

    async def list_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Application], int]:
        base = select(Application).where(Application.user_id == user_id)
        total = (await self.db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
        result = await self.db.execute(
            base.order_by(Application.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[ApplicationStatus] = None,
    ) -> tuple[list[Application], int]:
        base = select(Application)
        if status:
            base = base.where(Application.status == status)
        total = (await self.db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
        result = await self.db.execute(
            base.order_by(Application.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total
