from typing import Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.program import Program, ProgramCategory
from app.schemas.program import ProgramCreate, ProgramUpdate


class ProgramRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, program_id: int) -> Optional[Program]:
        result = await self.db.execute(select(Program).where(Program.id == program_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Program]:
        result = await self.db.execute(select(Program).where(Program.slug == slug))
        return result.scalar_one_or_none()

    async def create(self, data: ProgramCreate) -> Program:
        program = Program(**data.model_dump())
        self.db.add(program)
        await self.db.flush()
        await self.db.refresh(program)
        return program

    async def update(self, program: Program, data: ProgramUpdate) -> Program:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(program, field, value)
        await self.db.flush()
        await self.db.refresh(program)
        return program

    async def delete(self, program: Program) -> None:
        await self.db.delete(program)
        await self.db.flush()

    async def increment_views(self, program: Program) -> None:
        program.views_count += 1
        await self.db.flush()

    async def list_programs(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[ProgramCategory] = None,
        published_only: bool = True,
        search: Optional[str] = None,
    ) -> tuple[list[Program], int]:
        query = select(Program)

        if published_only:
            query = query.where(Program.is_published.is_(True))
        if category:
            query = query.where(Program.category == category)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Program.title.ilike(pattern),
                    Program.short_description.ilike(pattern),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Program.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        programs = list(result.scalars().all())
        return programs, total
