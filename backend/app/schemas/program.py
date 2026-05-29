from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.program import ProgramCategory, ProgramLevel


# ── Base ──────────────────────────────────────────────────────────────────────

class ProgramBase(BaseModel):
    title: str
    category: ProgramCategory
    level: ProgramLevel = ProgramLevel.BEGINNER
    short_description: str
    description: str
    duration_months: Optional[int] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    language_requirement: Optional[str] = None
    salary_range: Optional[str] = None
    cover_image_url: Optional[str] = None


# ── Create / Update ───────────────────────────────────────────────────────────

class ProgramCreate(ProgramBase):
    slug: str
    is_published: bool = False


class ProgramUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[ProgramCategory] = None
    level: Optional[ProgramLevel] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    duration_months: Optional[int] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    language_requirement: Optional[str] = None
    salary_range: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_published: Optional[bool] = None


# ── Response ──────────────────────────────────────────────────────────────────

class ProgramResponse(ProgramBase):
    id: int
    slug: str
    is_published: bool
    views_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProgramListResponse(BaseModel):
    items: list[ProgramResponse]
    total: int
    page: int
    size: int
