from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_admin
from app.db.session import get_db
from app.models.application import ApplicationStatus
from app.models.user import User
from app.repositories.application_repo import ApplicationRepository
from app.repositories.program_repo import ProgramRepository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationUpdate,
)

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_to_program(
    payload: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit an application for a program. One application per user per program."""
    prog_repo = ProgramRepository(db)
    program = await prog_repo.get_by_id(payload.program_id)
    if not program or not program.is_published:
        raise HTTPException(status_code=404, detail="Program not found")

    app_repo = ApplicationRepository(db)
    existing = await app_repo.get_by_user_and_program(current_user.id, payload.program_id)
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this program")

    return await app_repo.create(current_user.id, payload)


@router.get("/my", response_model=ApplicationListResponse)
async def my_applications(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List the current user's applications."""
    repo = ApplicationRepository(db)
    skip = (page - 1) * size
    apps, total = await repo.list_by_user(current_user.id, skip=skip, limit=size)
    return ApplicationListResponse(items=apps, total=total, page=page, size=size)


@router.get("/my/{app_id}", response_model=ApplicationResponse)
async def get_my_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get details of one of the current user's applications."""
    repo = ApplicationRepository(db)
    application = await repo.get_by_id(app_id)
    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.delete("/my/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def withdraw_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Withdraw (delete) an application. Only allowed if status is PENDING."""
    repo = ApplicationRepository(db)
    application = await repo.get_by_id(app_id)
    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.status != ApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending applications can be withdrawn")
    await repo.delete(application)


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.get("", response_model=ApplicationListResponse)
async def list_all_applications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: ApplicationStatus | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """[Admin] List all applications with optional status filter."""
    repo = ApplicationRepository(db)
    skip = (page - 1) * size
    apps, total = await repo.list_all(skip=skip, limit=size, status=status_filter)
    return ApplicationListResponse(items=apps, total=total, page=page, size=size)


@router.patch("/{app_id}", response_model=ApplicationResponse)
async def update_application_status(
    app_id: int,
    payload: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """[Admin] Update the status or add an admin note to an application."""
    repo = ApplicationRepository(db)
    application = await repo.get_by_id(app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return await repo.update(application, payload)
