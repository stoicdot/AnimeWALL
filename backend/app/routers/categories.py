
"""Public API endpoints for AnimeWall categories."""

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import Category
from app.models.wallpaper import Wallpaper
from app.schemas.category import CategoryListResponse, CategoryRead


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=CategoryListResponse,
    summary="List active wallpaper categories",
)
async def list_categories(
    session: AsyncSession = Depends(get_db),
) -> CategoryListResponse:
    """Return active categories with their published wallpaper counts."""

    wallpaper_count = func.count(Wallpaper.id).label("wallpaper_count")

    statement = (
        select(Category, wallpaper_count)
        .outerjoin(
            Wallpaper,
            and_(
                Wallpaper.category_id == Category.id,
                Wallpaper.is_active.is_(True),
                Wallpaper.rights_verified.is_(True),
                Wallpaper.deleted_at.is_(None),
            ),
        )
        .where(Category.is_active.is_(True))
        .group_by(Category.id)
        .order_by(Category.sort_order.asc(), Category.name.asc())
    )

    result = await session.execute(statement)
    rows = result.all()

    categories = [
        CategoryRead(
            id=category.id,
            slug=category.slug,
            name=category.name,
            kanji=category.kanji,
            romaji=category.romaji,
            description=category.description,
            accent_color=category.accent_color,
            sort_order=category.sort_order,
            wallpaper_count=count,
        )
        for category, count in rows
    ]

    return CategoryListResponse(data=categories)
