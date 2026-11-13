"""Tests for Phase 2 system health endpoints."""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.main import app


class HealthySession:
    async def execute(self, _statement):
        return 1


class UnhealthySession:
    async def execute(self, _statement):
        raise SQLAlchemyError("simulated database outage")


async def healthy_session_override():
    yield HealthySession()


async def unhealthy_session_override():
    yield UnhealthySession()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_liveness_does_not_require_database(client):
    response = await client.get("/api/health/live")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "alive"
    assert response.headers.get("x-request-id")


@pytest.mark.asyncio
async def test_readiness_returns_ready_when_database_query_succeeds(client):
    app.dependency_overrides[get_db] = healthy_session_override
    response = await client.get("/api/health/ready")
    assert response.status_code == 200
    assert response.json()["data"]["database"] == "connected"


@pytest.mark.asyncio
async def test_readiness_hides_database_exception_details(client):
    app.dependency_overrides[get_db] = unhealthy_session_override
    response = await client.get("/api/health/ready")
    payload = response.json()
    assert response.status_code == 503
    assert payload["error"]["code"] == "DATABASE_UNAVAILABLE"
    assert "simulated database outage" not in response.text


@pytest.mark.asyncio
async def test_openapi_document_is_available(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/health/live" in response.json()["paths"]


@pytest.mark.asyncio
async def test_unknown_route_uses_standard_error_envelope(client):
    response = await client.get("/route-that-does-not-exist")
    payload = response.json()
    assert response.status_code == 404
    assert payload["error"]["code"] == "HTTP_404"
    assert payload["error"]["request_id"] == response.headers["x-request-id"]


@pytest.mark.asyncio
async def test_cors_allows_only_a_configured_frontend_origin(client):
    allowed = await client.options(
        "/api/health/live",
        headers={
            "Origin": "http://localhost",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost"

    denied = await client.options(
        "/api/health/live",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in denied.headers
