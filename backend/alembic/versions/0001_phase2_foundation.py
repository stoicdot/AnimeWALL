"""Establish the Alembic migration baseline for Phase 2.

Revision ID: 0001_phase2
Revises:
Create Date: 2026-11-12

This is intentionally an empty baseline. Business tables are introduced in
subsequent feature migrations after their SQLAlchemy models are implemented.
"""
from typing import Sequence, Union

revision: str = "0001_phase2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No application tables exist in Phase 2."""
    pass


def downgrade() -> None:
    """No application tables exist in Phase 2."""
    pass
