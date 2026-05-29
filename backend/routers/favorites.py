from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.favorite import Favorite
from models.program import Program
from models.user import User
from schemas.program import ProgramResponse
from utils.dependencies import get_current_active_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])


# ── Response schemas (inline, lightweight) ────────────────────────────────────

class FavoriteResponse(BaseModel):
    id: int
    program_id: int
    program: ProgramResponse

    model_config = {"from_attributes": True}


class FavoriteListResponse(BaseModel):
    items: list[FavoriteResponse]
    total: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=FavoriteListResponse)
async def list_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return all programs saved as favourites by the current user."""
    result = await db.execute(
        select(Favorite).where(Favorite.user_id == current_user.id)
    )
    favorites = list(result.scalars().all())
    return FavoriteListResponse(items=favorites, total=len(favorites))


@router.post("/{program_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a program to the current user's favourites."""
    # Verify program exists
    program = (
        await db.execute(select(Program).where(Program.id == program_id))
    ).scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    # Check for existing favourite
    existing = (
        await db.execute(
            select(Favorite).where(
                Favorite.user_id == current_user.id,
                Favorite.program_id == program_id,
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Program already in favourites")

    fav = Favorite(user_id=current_user.id, program_id=program_id)
    db.add(fav)
    await db.flush()
    return {"detail": "Added to favourites", "favorite_id": fav.id}


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Remove a program from the current user's favourites."""
    fav = (
        await db.execute(
            select(Favorite).where(
                Favorite.user_id == current_user.id,
                Favorite.program_id == program_id,
            )
        )
    ).scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favourite not found")
    await db.delete(fav)
