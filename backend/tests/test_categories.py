
"""Tests for the AnimeWall category API."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.main import app


class FakeResult:
    """Simulate the result returned by SQLAlchemy."""

    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class FakeSession:
    """Simulate an asynchronous database session."""

    def __init__(self, rows):
        self.rows = rows

    async def execute(self, _statement):
        return FakeResult(self.rows)


def make_category(
    slug,
    name,
    sort_order,
    wallpaper_count,
):
    """Create a lightweight category object for testing."""

    category = SimpleNamespace(
        id=uuid4(),
        slug=slug,
        name=name,
        kanji=None,
        romaji=None,
        description=f"{name} aesthetic category",
        accent_color="#4A6B56",
        sort_order=sort_order,
    )

    return category, wallpaper_count


@pytest.fixture
async def client():
    """Create an isolated HTTP test client."""

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_categories_returns_category_data(client):
    rows = [
        make_category("nature", "Nature", 1, 5),
        make_category("cyberpunk", "Cyberpunk", 2, 3),
    ]

    async def override_database():
        yield FakeSession(rows)

    app.dependency_overrides[get_db] = override_database

    response = await client.get("/api/categories")

    assert response.status_code == 200

    payload = response.json()
    categories = payload["data"]

    assert len(categories) == 2
    assert categories[0]["slug"] == "nature"
    assert categories[0]["wallpaper_count"] == 5
    assert categories[1]["slug"] == "cyberpunk"
    assert categories[1]["wallpaper_count"] == 3


@pytest.mark.asyncio
async def test_categories_returns_empty_list_when_no_categories_exist(client):
    async def override_database():
        yield FakeSession([])

    app.dependency_overrides[get_db] = override_database

    response = await client.get("/api/categories")

    assert response.status_code == 200
    assert response.json() == {"data": []}


@pytest.mark.asyncio
async def test_categories_endpoint_exists_in_openapi(client):
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/categories" in response.json()["paths"]
