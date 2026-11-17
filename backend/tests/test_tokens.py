
"""Tests for JWT access token generation and verification."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.services.tokens import (
    create_access_token,
    decode_access_token,
)


TEST_USER_ID = "321c7b5e-fc98-46e1-a30e-37ef4eafdaf1"


def make_signed_token(payload):
    """Create a test token using the configured signing key."""

    secret = settings.jwt_secret_key

    if secret is None:
        raise RuntimeError("Test JWT secret is not configured.")

    return jwt.encode(
        payload,
        secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def test_access_token_can_be_created_and_decoded():
    token = create_access_token(
        subject=TEST_USER_ID,
        token_version=0,
    )

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == TEST_USER_ID
    assert payload["type"] == "access"
    assert payload["token_version"] == 0
    assert "exp" in payload
    assert "iat" in payload


def test_invalid_signature_is_rejected():
    token = jwt.encode(
        {
            "sub": TEST_USER_ID,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            "type": "access",
            "token_version": 0,
        },
        "wrong-test-signing-key-not-used-anywhere-1234567890",
        algorithm="HS256",
    )

    assert decode_access_token(token) is None

def test_expired_token_is_rejected():
    now = datetime.now(timezone.utc)

    token = make_signed_token(
        {
            "sub": TEST_USER_ID,
            "iat": now - timedelta(minutes=2),
            "exp": now - timedelta(minutes=1),
            "type": "access",
            "token_version": 0,
        }
    )

    assert decode_access_token(token) is None


def test_refresh_token_type_is_rejected():
    now = datetime.now(timezone.utc)

    token = make_signed_token(
        {
            "sub": TEST_USER_ID,
            "iat": now,
            "exp": now + timedelta(minutes=5),
            "type": "refresh",
            "token_version": 0,
        }
    )

    assert decode_access_token(token) is None


def test_malformed_token_is_rejected():
    assert decode_access_token("this-is-not-a-valid-jwt") is None


def test_negative_token_version_is_rejected():
    with pytest.raises(ValueError):
        create_access_token(
            subject=TEST_USER_ID,
            token_version=-1,
        )


def test_non_future_expiry_is_rejected():
    with pytest.raises(ValueError):
        create_access_token(
            subject=TEST_USER_ID,
            token_version=0,
            expires_delta=timedelta(seconds=-1),
        )


def test_missing_jwt_secret_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret_key", None)

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_access_token(
            subject=TEST_USER_ID,
            token_version=0,
        )
