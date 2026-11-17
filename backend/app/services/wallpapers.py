
"""Wallpaper business logic for AnimeWall."""

from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import APIError
from app.models.category import Category
from app.models.user import User
from app.models.wallpaper import Wallpaper
from app.schemas.wallpaper import (
    WallpaperCreate,
    WallpaperListResponse,
    WallpaperRead,
)


async def create_wallpaper(
    session: AsyncSession,
    *,
    payload: WallpaperCreate,
    current_user: User,
) -> Wallpaper:
    """Create an unpublished wallpaper submission."""

    try:
        category_statement = select(Category).where(
            Category.id == payload.category_id,
            Category.is_active.is_(True),
        )

        category = await session.scalar(category_statement)

        if category is None:
            raise APIError(
                status_code=404,
                code="CATEGORY_NOT_FOUND",
                message="The selected category does not exist or is inactive.",
            )

        wallpaper = Wallpaper(
            public_id=f"wall-{uuid4().hex}",
            title=payload.title,
            description=payload.description,
            anime_name=payload.anime_name,
            artist_name=payload.artist_name,
            category_id=category.id,
            created_by=current_user.id,
            width=payload.width,
            height=payload.height,
            aspect_ratio=payload.aspect_ratio,
            resolution_label=payload.resolution_label,
            orientation=payload.orientation,
            license_name=payload.license_name,
            license_url=str(payload.license_url) if payload.license_url else None,
            attribution_text=payload.attribution_text,
            source_url=str(payload.source_url) if payload.source_url else None,
            tags=payload.tags,
            colors=payload.colors,
            rights_verified=False,
            is_active=False,
            is_featured=False,
        )

        session.add(wallpaper)
        await session.flush()
        await session.commit()

        return wallpaper

    except IntegrityError:
        await session.rollback()
        raise APIError(
            status_code=409,
            code="WALLPAPER_CREATION_CONFLICT",
            message="The wallpaper could not be created due to a database conflict.",
        ) from None

    except Exception:
        await session.rollback()
        raise


async def list_public_wallpapers(
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
    category_id: UUID | None = None,
    search: str | None = None,
) -> WallpaperListResponse:
    """Return published and rights-verified wallpapers."""

    filters = [
        Wallpaper.is_active.is_(True),
        Wallpaper.rights_verified.is_(True),
        Wallpaper.deleted_at.is_(None),
    ]

    if category_id is not None:
        filters.append(Wallpaper.category_id == category_id)

    if search:
        search_term = f"%{search.strip()}%"
        filters.append(
            Wallpaper.title.ilike(search_term)
            | Wallpaper.anime_name.ilike(search_term)
        )

    count_statement = select(func.count(Wallpaper.id)).where(*filters)
    total = await session.scalar(count_statement)

    statement = (
        select(Wallpaper)
        .where(*filters)
        .order_by(
            Wallpaper.is_featured.desc(),
            Wallpaper.created_at.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    result = await session.scalars(statement)
    wallpapers = result.all()

    return WallpaperListResponse(
        data=[
            WallpaperRead.model_validate(wallpaper)
            for wallpaper in wallpapers
        ],
        total=total or 0,
    )


async def get_public_wallpaper(
    session: AsyncSession,
    *,
    public_id: str,
) -> Wallpaper:
    """Return one published and rights-verified wallpaper."""

    statement = select(Wallpaper).where(
        Wallpaper.public_id == public_id,
        Wallpaper.is_active.is_(True),
        Wallpaper.rights_verified.is_(True),
        Wallpaper.deleted_at.is_(None),
    )

    wallpaper = await session.scalar(statement)

    if wallpaper is None:
        raise APIError(
            status_code=404,
            code="WALLPAPER_NOT_FOUND",
            message="The requested wallpaper does not exist.",
        )

    return wallpaper
