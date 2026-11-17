
"""Tests for AnimeWall wallpaper business logic."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.models.wallpaper import Wallpaper
from app.schemas.wallpaper import WallpaperCreate
from app.services.wallpapers import create_wallpaper


class FakeTransaction:
    """Simulate an asynchronous database transaction."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


class FakeSession:
    """Simulate the database session used by wallpaper creation."""

    def __init__(self, category=None):
        self.category = category
        self.added_wallpaper = None

    def begin(self):
        return FakeTransaction()

    async def scalar(self, _statement):
        return self.category

    def add(self, wallpaper):
        self.added_wallpaper = wallpaper

    async def flush(self):
        pass


def make_category(*, is_active=True):
    return SimpleNamespace(
        id=uuid4(),
        is_active=is_active,
    )


def make_user():
    return SimpleNamespace(id=uuid4())


def make_payload(category_id):
    return WallpaperCreate(
        title="Anime Sunset",
        description="A beautiful anime sunset wallpaper.",
        anime_name="Original Anime",
        artist_name="Stoicdot",
        category_id=category_id,
        width=1920,
        height=1080,
        aspect_ratio="16:9",
        resolution_label="1080p",
        orientation="landscape",
        license_name="Permission Pending",
        tags=["sunset", "anime"],
        colors=["#FF5733", "#000000"],
    )


@pytest.mark.asyncio
async def test_create_wallpaper_successfully():
    category = make_category()
    user = make_user()
    session = FakeSession(category)

    wallpaper = await create_wallpaper(
        session,
        payload=make_payload(category.id),
        current_user=user,
    )

    assert isinstance(wallpaper, Wallpaper)
    assert session.added_wallpaper is wallpaper
    assert wallpaper.title == "Anime Sunset"
    assert wallpaper.anime_name == "Original Anime"


@pytest.mark.asyncio
async def test_create_wallpaper_assigns_authenticated_user():
    category = make_category()
    user = make_user()
    session = FakeSession(category)

    wallpaper = await create_wallpaper(
        session,
        payload=make_payload(category.id),
        current_user=user,
    )

    assert wallpaper.created_by == user.id


@pytest.mark.asyncio
async def test_create_wallpaper_stays_unpublished_by_default():
    category = make_category()
    user = make_user()
    session = FakeSession(category)

    wallpaper = await create_wallpaper(
        session,
        payload=make_payload(category.id),
        current_user=user,
    )

    assert wallpaper.is_active is False
    assert wallpaper.rights_verified is False
    assert wallpaper.is_featured is False


@pytest.mark.asyncio
async def test_create_wallpaper_rejects_missing_or_inactive_category():
    user = make_user()
    session = FakeSession(category=None)

    with pytest.raises(Exception) as error:
        await create_wallpaper(
            session,
            payload=make_payload(uuid4()),
            current_user=user,
        )

    assert getattr(error.value, "status_code", None) == 404
    assert session.added_wallpaper is None
class FakeSession:
    def __init__(self, category=None):
        self.category = category
        self.added_wallpaper = None
        self.committed = False
        self.rolled_back = False
        
    def add(self, obj):
        self.added_wallpaper = obj
        
    async def scalar(self, statement):
        return self.category

    async def flush(self):
        pass

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True