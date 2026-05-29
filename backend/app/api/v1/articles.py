from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_admin
from app.db.session import get_db
from app.models.article import Article
from app.models.user import User
from app.schemas.article import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
)

router = APIRouter(prefix="/articles", tags=["Articles"])


# ── Public endpoints ──────────────────────────────────────────────────────────

@router.get("", response_model=ArticleListResponse)
async def list_articles(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    search: Optional[str] = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db),
):
    """List published articles (blog / guides)."""
    base = select(Article).where(Article.is_published.is_(True))
    if search:
        p = f"%{search}%"
        base = base.where(or_(Article.title.ilike(p), Article.excerpt.ilike(p)))

    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    result = await db.execute(
        base.order_by(Article.created_at.desc()).offset((page - 1) * size).limit(size)
    )
    articles = list(result.scalars().all())
    return ArticleListResponse(items=articles, total=total, page=page, size=size)


@router.get("/{slug}", response_model=ArticleResponse)
async def get_article(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a single published article by slug. Increments view counter."""
    result = await db.execute(
        select(Article).where(Article.slug == slug, Article.is_published.is_(True))
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article.views_count += 1
    await db.flush()
    return article


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """[Admin] Create a new article."""
    existing = (
        await db.execute(select(Article).where(Article.slug == payload.slug))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    article = Article(**payload.model_dump(), author_id=current_admin.id)
    db.add(article)
    await db.flush()
    await db.refresh(article)
    return article


@router.patch("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    payload: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """[Admin] Update an article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(article, field, value)
    await db.flush()
    await db.refresh(article)
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """[Admin] Delete an article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    await db.delete(article)
