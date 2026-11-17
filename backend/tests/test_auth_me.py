
"""Tests for the authenticated user's profile endpoint."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.dependencies import get_current_user
from app.routers.auth import router as auth_router
from app.services.tokens import create_access_token


auth_me_app = FastAPI()
auth_me_app.include_router(auth_router, prefix="/api")


class FakeResult:
    def __init__(self, user):
        self.user = user

    def scalar_one_or_none(self):
        return self.user


class FakeSession:
    def __init__(self, user):
        self.user = user

    async def execute(self, _statement):
        return FakeResult(self.user)


def make_user(*, is_active=True, token_version=0):
    return SimpleNamespace(
        id=uuid4(),
        username="test_user",
        email="test@example.com",
        role="user",
        is_active=is_active,
        token_version=token_version,
    )


def make_token(user):
    return create_access_token(
        subject=user.id,
        token_version=user.token_version,
    )


def override_database(user):
    async def override_get_db():
        yield FakeSession(user)

    return override_get_db


@pytest.fixture
async def client():
    transport = ASGITransport(app=auth_me_app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    auth_me_app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_me_returns_authenticated_user(client):
    user = make_user()

    auth_me_app.dependency_overrides[get_db] = override_database(user)

    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {make_token(user)}"},
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["id"] == str(user.id)
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_me_rejects_missing_token(client):
    user = make_user()

    auth_me_app.dependency_overrides[get_db] = override_database(user)

    response = await client.get("/api/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_rejects_invalid_token(client):
    user = make_user()

    auth_me_app.dependency_overrides[get_db] = override_database(user)

    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_rejects_inactive_user(client):
    user = make_user(is_active=False)

    auth_me_app.dependency_overrides[get_db] = override_database(user)

    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {make_token(user)}"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_rejects_revoked_token(client):
    user = make_user(token_version=1)

    auth_me_app.dependency_overrides[get_db] = override_database(user)

    revoked_token = create_access_token(
        subject=user.id,
        token_version=0,
    )

    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {revoked_token}"},
    )

    assert response.status_code == 401
