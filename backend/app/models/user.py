
"""User database model."""
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Integer,
    String,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Registered AnimeWall user."""

    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'admin')",
            name="valid_role",
        ),
        CheckConstraint(
            "token_version >= 0",
            name="valid_token_version",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    username: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(16),
        default="user",
        server_default=text("'user'"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
    )

    token_version: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
    )
    wallpapers: Mapped[list["Wallpaper"]] = relationship(
        back_populates="creator"
    )

    def __repr__(self) -> str:
        return f"<User username={self.username!r}>"
