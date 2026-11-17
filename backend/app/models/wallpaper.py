
"""AnimeWall wallpaper database model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Wallpaper(Base, TimestampMixin):
    """Main wallpaper metadata and publishing information."""

    __tablename__ = "wallpapers"

    __table_args__ = (
        CheckConstraint(
            "width > 0 AND height > 0",
            name="positive_dimensions",
        ),
        CheckConstraint(
            "orientation IN ('landscape', 'portrait', 'ultrawide')",
            name="valid_orientation",
        ),
        CheckConstraint(
            "download_count >= 0 AND favorite_count >= 0 "
            "AND view_count >= 0",
            name="nonnegative_counters",
        ),
        Index(
            "ix_wallpapers_category_active",
            "category_id",
            "is_active",
        ),
        Index(
            "ix_wallpapers_active_popularity",
            "is_active",
            "download_count",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    public_id: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    anime_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    artist_name: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    category_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )

    created_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    aspect_ratio: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    resolution_label: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        index=True,
    )

    orientation: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        index=True,
    )

    license_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    license_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    attribution_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    rights_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
        index=True,
    )

    download_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        server_default=text("0"),
        nullable=False,
    )

    favorite_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        server_default=text("0"),
        nullable=False,
    )

    view_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        server_default=text("0"),
        nullable=False,
    )

    tags: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        server_default=text("'[]'::jsonb"),
        nullable=False,
    )

    colors: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        server_default=text("'[]'::jsonb"),
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    storage_cleanup_pending: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(
        back_populates="wallpapers",
    )

    creator: Mapped["User | None"] = relationship(
        back_populates="wallpapers",
    )
    assets: Mapped[list["WallpaperAsset"]] = relationship(
        back_populates="wallpaper"
    )
    rights_records: Mapped[list["WallpaperRights"]] = relationship(
        back_populates="wallpaper",
    )

    def __repr__(self) -> str:
        return f"<Wallpaper title={self.title!r}>"
