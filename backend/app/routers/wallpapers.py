
"""Wallpaper API endpoints for AnimeWall."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.wallpaper import (
    WallpaperCreate,
    WallpaperDetailResponse,
    WallpaperListResponse,
    WallpaperRead,
)
from app.services.wallpapers import (
    create_wallpaper,
    list_public_wallpapers,
)
from app.services.wallpapers import (
    create_wallpaper,
    list_public_wallpapers,
    get_public_wallpaper,
)


router = APIRouter(prefix="/wallpapers", tags=["Wallpapers"])


@router.post(
    "",
    response_model=WallpaperDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new wallpaper",
)
async def submit_wallpaper(
    payload: WallpaperCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WallpaperDetailResponse:
    """Create an unpublished wallpaper submission."""

    wallpaper = await create_wallpaper(
        session,
        payload=payload,
        current_user=current_user,
    )

    return WallpaperDetailResponse(
        data=WallpaperRead.model_validate(wallpaper)
    )


@router.get(
    "",
    response_model=WallpaperListResponse,
    summary="List published wallpapers",
)
async def get_wallpapers(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category_id: UUID | None = None,
    search: str | None = Query(default=None, min_length=1, max_length=120),
    session: AsyncSession = Depends(get_db),
) -> WallpaperListResponse:
    """Return published wallpapers with optional filters."""

    return await list_public_wallpapers(
        session,
        limit=limit,
        offset=offset,
        category_id=category_id,
        search=search,
    )

@router.get(
    "/{public_id}",
    response_model=WallpaperDetailResponse,
    summary="Get wallpaper details",
)
async def get_wallpaper_details(
    public_id: str,
    session: AsyncSession = Depends(get_db),
) -> WallpaperDetailResponse:
    """Return details of a published wallpaper."""

    wallpaper = await get_public_wallpaper(
        session,
        public_id=public_id,
    )

    return WallpaperDetailResponse(
        data=WallpaperRead.model_validate(wallpaper)
    )
