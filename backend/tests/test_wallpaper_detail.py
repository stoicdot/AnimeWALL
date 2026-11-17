
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import APIError
from app.services.wallpapers import get_public_wallpaper


class FakeSession:
    def __init__(self, wallpaper=None):
        self.wallpaper = wallpaper
        self.statement = None

    async def scalar(self, statement):
        self.statement = statement
        return self.wallpaper


def make_wallpaper():
    return SimpleNamespace(
        id=uuid4(),
        public_id="wall-test123",
        title="Naruto Wallpaper",
        is_active=True,
        rights_verified=True,
        deleted_at=None,
    )


@pytest.mark.asyncio
async def test_get_public_wallpaper_successfully():
    wallpaper = make_wallpaper()
    session = FakeSession(wallpaper)

    result = await get_public_wallpaper(
        session,
        public_id="wall-test123",
    )

    assert result == wallpaper
    assert result.public_id == "wall-test123"


@pytest.mark.asyncio
async def test_get_public_wallpaper_not_found():
    session = FakeSession()

    with pytest.raises(APIError) as exc:
        await get_public_wallpaper(
            session,
            public_id="wall-invalid",
        )

    assert exc.value.status_code == 404
    assert exc.value.code == "WALLPAPER_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_public_wallpaper_filters_by_public_id():
    session = FakeSession(make_wallpaper())

    await get_public_wallpaper(
        session,
        public_id="wall-test123",
    )

    query = str(session.statement)

    assert "wallpapers.public_id" in query


@pytest.mark.asyncio
async def test_get_public_wallpaper_requires_active_status():
    session = FakeSession(make_wallpaper())

    await get_public_wallpaper(
        session,
        public_id="wall-test123",
    )

    query = str(session.statement)

    assert "wallpapers.is_active" in query


@pytest.mark.asyncio
async def test_get_public_wallpaper_requires_verified_rights():
    session = FakeSession(make_wallpaper())

    await get_public_wallpaper(
        session,
        public_id="wall-test123",
    )

    query = str(session.statement)

    assert "wallpapers.rights_verified" in query
    assert "wallpapers.deleted_at" in query
