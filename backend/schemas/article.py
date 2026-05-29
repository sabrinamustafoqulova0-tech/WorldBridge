from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ArticleCreate(BaseModel):
    slug: str
    title: str
    excerpt: str
    content: str
    cover_image_url: Optional[str] = None
    is_published: bool = False


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_published: Optional[bool] = None


class ArticleResponse(BaseModel):
    id: int
    slug: str
    title: str
    excerpt: str
    content: str
    cover_image_url: Optional[str] = None
    author_id: Optional[int] = None
    is_published: bool
    views_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ArticleListResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    page: int
    size: int
