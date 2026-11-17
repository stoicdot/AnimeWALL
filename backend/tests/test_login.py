
"""Tests for AnimeWall login API."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.main import app
from app.services.security import hash_password
from app.services.tokens import decode_access_token


TEST_PASSWORD = "AnimeWall-Test-Password-123!"


class FakeSession:
    def __init__(self, user=None):
        self.user = user

    async def scalar(self, _statement):
        return self.user


def make_user(*, is_active=True):
    return SimpleNamespace(
        id=uuid4(),
        username="stoic_user",
        email="test@example.com",
        password_hash=hash_password(TEST_PASSWORD),
        role="user",
        token_version=0,
        is_active=is_active,
    )


def override_database(session):
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_with_correct_credentials(client):
    user = make_user()
    override_database(FakeSession(user))

    response = await client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    payload = response.json()["data"]

    assert payload["user"]["username"] == "stoic_user"
    assert payload["user"]["role"] == "user"
    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] == 900

    claims = decode_access_token(payload["access_token"])

    assert claims is not None
    assert claims["sub"] == str(user.id)
    assert claims["token_version"] == 0


@pytest.mark.asyncio
async def test_login_rejects_incorrect_password(client):
    user = make_user()
    override_database(FakeSession(user))

    response = await client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "Wrong-Password-123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_rejects_unknown_email(client):
    override_database(FakeSession(None))

    response = await client.post(
        "/api/auth/login",
        json={
            "email": "unknown@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_rejects_inactive_user(client):
    user = make_user(is_active=False)
    override_database(FakeSession(user))

    response = await client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_does_not_reveal_account_existence(client):
    override_database(FakeSession(None))

    unknown_response = await client.post(
        "/api/auth/login",
        json={
            "email": "unknown@example.com",
            "password": TEST_PASSWORD,
        },
    )

    user = make_user()
    override_database(FakeSession(user))

    wrong_password_response = await client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "Wrong-Password-123!",
        },
    )

    unknown_error = unknown_response.json()["error"]
    wrong_password_error = wrong_password_response.json()["error"]

    assert unknown_response.status_code == 401
    assert wrong_password_response.status_code == 401
    assert unknown_error["code"] == wrong_password_error["code"]
    assert unknown_error["message"] == wrong_password_error["message"]
