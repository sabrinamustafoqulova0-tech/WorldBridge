from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Favorite(Base):
    """A user's saved / favourite program."""
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "program_id", name="uq_favorite_user_program"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    program_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="favorites")
    program = relationship("Program", back_populates="favorites")

    def __repr__(self) -> str:
        return f"<Favorite user_id={self.user_id} program_id={self.program_id}>"
