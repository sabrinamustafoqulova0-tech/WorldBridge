import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ProgramCategory(str, enum.Enum):
    AUSBILDUNG = "ausbildung"
    FSJ = "fsj"
    AU_PAIR = "au_pair"
    SCHULE = "schule"
    ARBEIT = "arbeit"
    STUDIUM = "studium"


class ProgramLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[ProgramCategory] = mapped_column(
        Enum(ProgramCategory, name="program_category"), nullable=False, index=True
    )
    level: Mapped[ProgramLevel] = mapped_column(
        Enum(ProgramLevel, name="program_level"),
        nullable=False,
        default=ProgramLevel.BEGINNER,
    )
    short_description: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language_requirement: Mapped[str | None] = mapped_column(String(100), nullable=True)
    salary_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    applications = relationship("Application", back_populates="program", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Program id={self.id} slug={self.slug!r} category={self.category}>"
