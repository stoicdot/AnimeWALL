
"""Rights and licensing records for AnimeWall wallpapers."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class WallpaperRights(Base, TimestampMixin):
    """Individual copyright or licensing permission record."""

    __tablename__ = "wallpaper_rights"

    __table_args__ = (
        CheckConstraint(
            "rights_type IN ('artwork', 'character_ip', 'trademark', 'other')",
            name="valid_rights_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'verified', 'rejected', 'revoked')",
            name="valid_status",
        ),
        CheckConstraint(
            "territory_scope IN ('worldwide', 'restricted', 'unknown')",
            name="valid_territory_scope",
        ),
        CheckConstraint(
            "expires_at IS NULL OR granted_at IS NULL "
            "OR expires_at > granted_at",
            name="valid_expiry_date",
        ),
        Index(
            "ix_wallpaper_rights_wallpaper_status",
            "wallpaper_id",
            "status",
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
    )

    rights_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    rights_holder_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    license_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    license_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Private storage path for permission documents or evidence.
    # Never expose this path through public API responses.
    permission_evidence_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    public_display_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    commercial_use_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    downloads_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    modifications_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )

    attribution_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
    )

    required_credit: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    territory_scope: Mapped[str] = mapped_column(
        String(20),
        default="unknown",
        server_default=text("'unknown'"),
        nullable=False,
    )

    territory_details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    granted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(16),
        default="pending",
        server_default=text("'pending'"),
        nullable=False,
    )

    submitted_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    reviewed_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    review_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    wallpaper: Mapped["Wallpaper"] = relationship(
        back_populates="rights_records",
    )

    submitted_by_user: Mapped["User | None"] = relationship(
        foreign_keys=[submitted_by],
        back_populates="submitted_rights_records",
    )

    reviewer: Mapped["User | None"] = relationship(
        foreign_keys=[reviewed_by],
        back_populates="reviewed_rights_records",
    )

    def __repr__(self) -> str:
        return (
            f"<WallpaperRights type={self.rights_type!r} "
            f"status={self.status!r}>"
        )
