
"""Tests for authenticated user and admin dependencies."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.user import User
from app.services.tokens import create_access_token


test_app = FastAPI()


@test_app.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
):
    return {"user_id": str(current_user.id)}


@test_app.get("/admin")
async def admin_route(
    current_user: User = Depends(get_current_admin),
):
    return {"username": current_user.username}


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


def make_user(
    *,
    role="user",
    is_active=True,
    token_version=0,
    user_id=None,
):
    return SimpleNamespace(
        id=user_id or uuid4(),
        username="test_user",
        role=role,
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
    transport = ASGITransport(app=test_app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_authenticated_user_can_access_protected_route(client):
    user = make_user()

    test_app.dependency_overrides[get_db] = override_database(user)

    response = await client.get(
        "/protected",
        headers={"Authorization": f"Bearer {make_token(user)}"},
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == str(user.id)


@pytest.mark.asyncio
async def test_missing_token_is_rejected(client):
    user = make_user()

    test_app.dependency_overrides[get_db] = override_database(user)

    response = await client.get("/protected")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_is_rejected(client):
    user = make_user()

    test_app.dependency_overrides[get_db] = override_database(user)

    response = await client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unknown_user_is_rejected(client):
    test_app.dependency_overrides[get_db] = override_database(None)

    user_id = uuid4()
    token = create_access_token(user_id, token_version=0)

    response = await client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_inactive_user_is_rejected(client):
    user = make_user(is_active=False)

    test_app.dependency_overrides[get_db] = override_database(user)

    response = await client.get(
        "/protected",
        headers={"Authorization": f"Bearer {make_token(user)}"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_outdated_token_version_is_rejected(client):
    user = make_user(token_version=1)

    test_app.dependency_overrides[get_db] = override_database(user)

    token = create_access_token(
        subject=user.id,
        token_version=0,
    )

    response = await client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_can_access_admin_route(client):
    admin = make_user(role="admin")

    test_app.dependency_overrides[get_db] = override_database(admin)

    response = await client.get(
        "/admin",
        headers={"Authorization": f"Bearer {make_token(admin)}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "test_user"


@pytest.mark.asyncio
async def test_normal_user_cannot_access_admin_route(client):
    user = make_user(role="user")

    test_app.dependency_overrides[get_db] = override_database(user)

    response = await client.get(
        "/admin",
        headers={"Authorization": f"Bearer {make_token(user)}"},
    )

    assert response.status_code == 403
