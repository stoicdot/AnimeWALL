
"""Wallpaper image asset database model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WallpaperAsset(Base):

    __tablename__ = "wallpaper_assets"

    __table_args__ = (
        UniqueConstraint(
            "wallpaper_id",
            "variant",
            name="uq_wallpaper_assets_wallpaper_variant",
        ),
        CheckConstraint(
            "width > 0 AND height > 0",
            name="positive_dimensions",
        ),
        CheckConstraint(
            "size_bytes > 0",
            name="positive_size_bytes",
        ),
        CheckConstraint(
            "variant IN ('thumbnail', 'preview', 'original', '2k', '1080p', 'mobile')",
            name="valid_variant",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    wallpaper_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("wallpapers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    variant: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    bucket: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    object_path: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
    )

    width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    checksum_sha256: Mapped[str | None] = mapped_column(
        CHAR(64),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    wallpaper: Mapped["Wallpaper"] = relationship(
        back_populates="assets",
    )
