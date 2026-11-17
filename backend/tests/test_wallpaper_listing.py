
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.wallpapers import list_public_wallpapers


class FakeResult:
    def __init__(self, wallpapers):
        self.wallpapers = wallpapers

    def all(self):
        return self.wallpapers


class FakeSession:
    def __init__(self, wallpapers=None, total=None):
        self.wallpapers = wallpapers or []
        self.total = total
        self.statements = []

    async def scalar(self, statement):
        self.statements.append(statement)
        return self.total

    async def scalars(self, statement):
        self.statements.append(statement)
        return FakeResult(self.wallpapers)


def make_wallpaper():
    return SimpleNamespace(
        id=uuid4(),
        public_id="wall-test123",
        title="Naruto Wallpaper",
        description="Test wallpaper",
        anime_name="Naruto",
        artist_name="Stoicdot",
        category_id=uuid4(),
        width=1920,
        height=1080,
        aspect_ratio="16:9",
        resolution_label="Full HD",
        orientation="landscape",
        license_name="Test License",
        license_url=None,
        attribution_text=None,
        source_url=None,
        is_featured=False,
        download_count=0,
        favorite_count=0,
        view_count=0,
        tags=["anime", "naruto"],
        colors=["#000000"],
    )


@pytest.mark.asyncio
async def test_list_public_wallpapers_successfully():
    wallpaper = make_wallpaper()
    session = FakeSession([wallpaper], total=1)

    response = await list_public_wallpapers(session)

    assert response.total == 1
    assert len(response.data) == 1
    assert response.data[0].title == "Naruto Wallpaper"


@pytest.mark.asyncio
async def test_list_public_wallpapers_returns_empty_result():
    session = FakeSession([], total=0)

    response = await list_public_wallpapers(session)

    assert response.total == 0
    assert response.data == []


@pytest.mark.asyncio
async def test_list_public_wallpapers_applies_category_filter():
    session = FakeSession([], total=0)
    category_id = uuid4()

    await list_public_wallpapers(
        session,
        category_id=category_id,
    )

    query = str(session.statements[1])

    assert "wallpapers.category_id" in query
    assert str(category_id) in str(session.statements[1].compile().params.values())


@pytest.mark.asyncio
async def test_list_public_wallpapers_applies_search_filter():
    session = FakeSession([], total=0)

    await list_public_wallpapers(
        session,
        search="Naruto",
    )

    query = str(session.statements[1])

    assert "wallpapers.title" in query
    assert "wallpapers.anime_name" in query
    assert "%Naruto%" in str(session.statements[1].compile().params.values())


@pytest.mark.asyncio
async def test_list_public_wallpapers_applies_pagination():
    session = FakeSession([], total=0)

    await list_public_wallpapers(
        session,
        limit=10,
        offset=20,
    )

    statement = session.statements[1]

    assert statement._limit_clause.value == 10
    assert statement._offset_clause.value == 20
