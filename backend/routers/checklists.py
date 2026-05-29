from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.checklist import ChecklistItem
from models.user import User
from utils.dependencies import get_current_active_user

router = APIRouter(prefix="/checklists", tags=["Checklists"])


# ── Inline schemas ────────────────────────────────────────────────────────────

class ChecklistItemCreate(BaseModel):
    title: str
    program_id: Optional[int] = None
    position: int = 0


class ChecklistItemUpdate(BaseModel):
    title: Optional[str] = None
    is_done: Optional[bool] = None
    position: Optional[int] = None


class ChecklistItemResponse(BaseModel):
    id: int
    user_id: int
    program_id: Optional[int] = None
    title: str
    is_done: bool
    position: int

    model_config = {"from_attributes": True}


class ChecklistListResponse(BaseModel):
    items: list[ChecklistItemResponse]
    total: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=ChecklistListResponse)
async def list_checklist_items(
    program_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the current user's checklist items, optionally filtered by program."""
    stmt = select(ChecklistItem).where(ChecklistItem.user_id == current_user.id)
    if program_id is not None:
        stmt = stmt.where(ChecklistItem.program_id == program_id)
    result = await db.execute(stmt.order_by(ChecklistItem.position))
    items = list(result.scalars().all())
    return ChecklistListResponse(items=items, total=len(items))


@router.post("", response_model=ChecklistItemResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist_item(
    payload: ChecklistItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new checklist item for the current user."""
    item = ChecklistItem(
        user_id=current_user.id,
        title=payload.title,
        program_id=payload.program_id,
        position=payload.position,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=ChecklistItemResponse)
async def update_checklist_item(
    item_id: int,
    payload: ChecklistItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a checklist item (title, done-state, or sort position)."""
    result = await db.execute(
        select(ChecklistItem).where(
            ChecklistItem.id == item_id,
            ChecklistItem.user_id == current_user.id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.flush()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a checklist item owned by the current user."""
    result = await db.execute(
        select(ChecklistItem).where(
            ChecklistItem.id == item_id,
            ChecklistItem.user_id == current_user.id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    await db.delete(item)
