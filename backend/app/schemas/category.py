
"""Response schemas for AnimeWall categories."""

from uuid import UUID

from pydantic import BaseModel


class CategoryRead(BaseModel):
    """Public category information."""

    id: UUID
    slug: str
    name: str
    kanji: str | None = None
    romaji: str | None = None
    description: str | None = None
    accent_color: str | None = None
    sort_order: int
    wallpaper_count: int = 0


class CategoryListResponse(BaseModel):
    """Standard response containing a list of categories."""

    data: list[CategoryRead]
