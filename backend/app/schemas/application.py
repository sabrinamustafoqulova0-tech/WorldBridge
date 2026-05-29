from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    program_id: int
    motivation_letter: Optional[str] = None
    cv_url: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    admin_note: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    program_id: int
    status: ApplicationStatus
    motivation_letter: Optional[str] = None
    cv_url: Optional[str] = None
    admin_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
    page: int
    size: int
