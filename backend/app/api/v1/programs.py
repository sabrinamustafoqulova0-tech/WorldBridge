from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_admin
from app.db.session import get_db
from app.models.program import ProgramCategory
from app.repositories.program_repo import ProgramRepository
from app.schemas.program import (
    ProgramCreate,
    ProgramListResponse,
    ProgramResponse,
    ProgramUpdate,
)

router = APIRouter(prefix="/programs", tags=["Programs"])


@router.get("", response_model=ProgramListResponse)
async def list_programs(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    category: Optional[ProgramCategory] = None,
    search: Optional[str] = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db),
):
    """List published programs with optional category filter and full-text search."""
    repo = ProgramRepository(db)
    skip = (page - 1) * size
    programs, total = await repo.list_programs(
        skip=skip, limit=size, category=category, published_only=True, search=search
    )
    return ProgramListResponse(items=programs, total=total, page=page, size=size)


@router.get("/{slug}", response_model=ProgramResponse)
async def get_program(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a single published program by its slug. Increments view counter."""
    repo = ProgramRepository(db)
    program = await repo.get_by_slug(slug)
    if not program or not program.is_published:
        raise HTTPException(status_code=404, detail="Program not found")
    await repo.increment_views(program)
    return program


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.post("", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
    payload: ProgramCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """[Admin] Create a new program."""
    repo = ProgramRepository(db)
    if await repo.get_by_slug(payload.slug):
        raise HTTPException(status_code=400, detail="Slug already exists")
    return await repo.create(payload)


@router.patch("/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: int,
    payload: ProgramUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """[Admin] Partially update a program."""
    repo = ProgramRepository(db)
    program = await repo.get_by_id(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return await repo.update(program, payload)


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """[Admin] Delete a program."""
    repo = ProgramRepository(db)
    program = await repo.get_by_id(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    await repo.delete(program)


@router.get("/admin/all", response_model=ProgramListResponse)
async def list_all_programs_admin(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[ProgramCategory] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """[Admin] List all programs including unpublished ones."""
    repo = ProgramRepository(db)
    skip = (page - 1) * size
    programs, total = await repo.list_programs(
        skip=skip, limit=size, category=category, published_only=False
    )
    return ProgramListResponse(items=programs, total=total, page=page, size=size)
