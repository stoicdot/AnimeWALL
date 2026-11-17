
"""Pydantic schemas for AnimeWall wallpapers."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class WallpaperCreate(BaseModel):
    """Input schema for submitting wallpaper metadata."""

    title: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=5000)

    anime_name: str = Field(min_length=1, max_length=120)
    artist_name: str | None = Field(default=None, max_length=120)

    category_id: UUID

    width: int = Field(gt=0)
    height: int = Field(gt=0)

    aspect_ratio: str = Field(min_length=1, max_length=16)
    resolution_label: str = Field(min_length=1, max_length=80)
    orientation: str

    license_name: str = Field(min_length=1, max_length=100)
    license_url: HttpUrl | None = None
    attribution_text: str | None = None
    source_url: HttpUrl | None = None

    tags: list[str] = Field(default_factory=list, max_length=30)
    colors: list[str] = Field(default_factory=list, max_length=10)


class WallpaperRead(BaseModel):
    """Public wallpaper metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    public_id: str
    title: str
    description: str | None
    anime_name: str
    artist_name: str | None
    category_id: UUID
    width: int
    height: int
    aspect_ratio: str
    resolution_label: str
    orientation: str
    license_name: str
    license_url: str | None
    attribution_text: str | None
    source_url: str | None
    is_featured: bool
    download_count: int
    favorite_count: int
    view_count: int
    tags: list[str]
    colors: list[str]


class WallpaperListResponse(BaseModel):
    """Response containing multiple wallpapers."""

    data: list[WallpaperRead]
    total: int


class WallpaperDetailResponse(BaseModel):
    """Response containing a single wallpaper."""

    data: WallpaperRead
