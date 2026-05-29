from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.program import Program, ProgramCategory
from models.user import User
from schemas.program import (
    ProgramCreate,
    ProgramListResponse,
    ProgramResponse,
    ProgramUpdate,
)
from utils.dependencies import get_current_admin

router = APIRouter(prefix="/programs", tags=["Programs"])


# ── Public endpoints ──────────────────────────────────────────────────────────

@router.get("", response_model=ProgramListResponse)
async def list_programs(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    category: Optional[ProgramCategory] = None,
    search: Optional[str] = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db),
):
    """List published programs with optional category filter and full-text search."""
    base = select(Program).where(Program.is_published.is_(True))
    if category:
        base = base.where(Program.category == category)
    if search:
        p = f"%{search}%"
        base = base.where(
            or_(Program.title.ilike(p), Program.short_description.ilike(p))
        )
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    result = await db.execute(
        base.order_by(Program.created_at.desc()).offset((page - 1) * size).limit(size)
    )
    programs = list(result.scalars().all())
    return ProgramListResponse(items=programs, total=total, page=page, size=size)


@router.get("/{slug}", response_model=ProgramResponse)
async def get_program(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a single published program by its slug. Increments view counter."""
    result = await db.execute(
        select(Program).where(Program.slug == slug, Program.is_published.is_(True))
    )
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    program.views_count += 1
    await db.flush()
    return program


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.post("", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
    payload: ProgramCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """[Admin] Create a new program."""
    existing = (
        await db.execute(select(Program).where(Program.slug == payload.slug))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    program = Program(**payload.model_dump())
    db.add(program)
    await db.flush()
    await db.refresh(program)
    return program


@router.patch("/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: int,
    payload: ProgramUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """[Admin] Partially update a program."""
    result = await db.execute(select(Program).where(Program.id == program_id))
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(program, field, value)
    await db.flush()
    await db.refresh(program)
    return program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """[Admin] Delete a program."""
    result = await db.execute(select(Program).where(Program.id == program_id))
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    await db.delete(program)


@router.get("/admin/all", response_model=ProgramListResponse)
async def list_all_programs_admin(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[ProgramCategory] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """[Admin] List all programs including unpublished ones."""
    base = select(Program)
    if category:
        base = base.where(Program.category == category)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    result = await db.execute(
        base.order_by(Program.created_at.desc()).offset((page - 1) * size).limit(size)
    )
    programs = list(result.scalars().all())
    return ProgramListResponse(items=programs, total=total, page=page, size=size)
