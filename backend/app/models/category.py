
"""AnimeWall category database model."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, Integer, String, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """Aesthetic category for organizing wallpapers."""

    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    slug: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    kanji: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    romaji: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    cover_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    accent_color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
        index=True,
    )
    wallpapers: Mapped[list["Wallpaper"]] = relationship(
        back_populates="category"
    )

    def __repr__(self) -> str:
        return f"<Category name={self.name!r}>"
