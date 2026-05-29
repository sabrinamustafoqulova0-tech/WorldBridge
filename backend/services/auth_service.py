from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.user import UserCreate, UserUpdate
from utils.jwt import hash_password


class AuthService:
    """
    Business-logic layer for user management and authentication.
    Keeps routers thin and testable.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Queries ───────────────────────────────────────────────────────────────

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_users(
        self, skip: int = 0, limit: int = 20
    ) -> Tuple[List[User], int]:
        total = (
            await self.db.execute(select(func.count(User.id)))
        ).scalar_one()
        result = await self.db.execute(
            select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total

    # ── Mutations ─────────────────────────────────────────────────────────────

    async def create_user(self, payload: UserCreate) -> User:
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            is_active=True,
            is_admin=False,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_user(self, user: User, payload: UserUpdate) -> User:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()
