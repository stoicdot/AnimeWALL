
"""JWT access token creation and verification."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings


def _get_secret() -> str:
    """Get the configured JWT secret without exposing it."""

    secret = settings.jwt_secret_key

    if secret is None or not secret.get_secret_value().strip():
        raise RuntimeError("JWT_SECRET_KEY is not configured.")

    return secret.get_secret_value()


def create_access_token(
    subject: UUID | str,
    token_version: int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a short-lived signed access token."""

    if token_version < 0:
        raise ValueError("Token version cannot be negative.")

    now = datetime.now(timezone.utc)
    expires_at = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    )

    if expires_at <= now:
        raise ValueError("Token expiry must be in the future.")

    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": expires_at,
        "type": "access",
        "token_version": token_version,
    }

    return jwt.encode(
        payload,
        _get_secret(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(
    token: str,
) -> dict[str, Any] | None:
    """Verify a JWT and return its claims, or None if invalid."""

    try:
        payload = jwt.decode(
            token,
            _get_secret(),
            algorithms=[settings.jwt_algorithm],
            options={
                "require": [
                    "sub",
                    "iat",
                    "exp",
                    "type",
                    "token_version",
                ]
            },
        )

        if payload.get("type") != "access":
            return None

        if not isinstance(payload.get("sub"), str):
            return None

        if not isinstance(payload.get("token_version"), int):
            return None

        if isinstance(payload.get("token_version"), bool):
            return None

        return payload

    except InvalidTokenError:
        return None
