
"""Tests for AnimeWall registration API."""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.main import app
from app.services.security import verify_password
from app.services.tokens import decode_access_token


class FakeTransaction:
    """Simulate an asynchronous database transaction."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


class FakeSession:
    """Simulate the database session used by registration."""

    def __init__(self, existing_user=None):
        self.existing_user = existing_user
        self.added_user = None

    def begin(self):
        return FakeTransaction()

    async def scalar(self, _statement):
        return self.existing_user

    def add(self, user):
        self.added_user = user

    async def flush(self):
        if self.added_user is not None:
            self.added_user.id = uuid4()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def override_database(session):
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db


def registration_payload(**overrides):
    payload = {
        "username": "Stoic_User",
        "email": "test@example.com",
        "password": "AnimeWall-Test-Password-123!",
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_register_creates_user_and_returns_access_token(client):
    session = FakeSession()
    override_database(session)

    response = await client.post(
        "/api/auth/register",
        json=registration_payload(),
    )

    assert response.status_code == 201

    payload = response.json()["data"]
    user_data = payload["user"]

    assert user_data["username"] == "stoic_user"
    assert user_data["email"] == "test@example.com"
    assert user_data["role"] == "user"

    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] == 900

    assert session.added_user is not None
    assert session.added_user.password_hash != (
        "AnimeWall-Test-Password-123!"
    )
    assert verify_password(
        "AnimeWall-Test-Password-123!",
        session.added_user.password_hash,
    )

    claims = decode_access_token(payload["access_token"])

    assert claims is not None
    assert claims["sub"] == str(session.added_user.id)


@pytest.mark.asyncio
async def test_register_rejects_existing_username_or_email(client):
    session = FakeSession(existing_user=object())
    override_database(session)

    response = await client.post(
        "/api/auth/register",
        json=registration_payload(),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ACCOUNT_ALREADY_EXISTS"
    assert session.added_user is None


@pytest.mark.asyncio
async def test_register_rejects_invalid_email(client):
    session = FakeSession()
    override_database(session)

    response = await client.post(
        "/api/auth/register",
        json=registration_payload(email="not-an-email"),
    )

    assert response.status_code == 422
    assert session.added_user is None


@pytest.mark.asyncio
async def test_register_rejects_short_password(client):
    session = FakeSession()
    override_database(session)

    response = await client.post(
        "/api/auth/register",
        json=registration_payload(password="short"),
    )

    assert response.status_code == 422
    assert session.added_user is None


@pytest.mark.asyncio
async def test_register_never_allows_self_assigned_admin_role(client):
    session = FakeSession()
    override_database(session)

    response = await client.post(
        "/api/auth/register",
        json=registration_payload(role="admin"),
    )

    assert response.status_code == 201
    assert response.json()["data"]["user"]["role"] == "user"


@pytest.mark.asyncio
async def test_register_rejects_invalid_username(client):
    session = FakeSession()
    override_database(session)

    response = await client.post(
        "/api/auth/register",
        json=registration_payload(username="bad username!"),
    )

    assert response.status_code == 422
    assert session.added_user is None
