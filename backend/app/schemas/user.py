from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ── Base ──────────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    full_name: str


# ── Create / Update ───────────────────────────────────────────────────────────

class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# ── Response ──────────────────────────────────────────────────────────────────

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    size: int
