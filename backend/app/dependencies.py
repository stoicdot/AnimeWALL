
"""Reusable FastAPI dependencies for database and authentication."""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.tokens import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Return the authenticated active user from a valid access token."""

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise unauthorized

    try:
        user_id = UUID(payload["sub"])
    except (ValueError, TypeError):
        raise unauthorized from None

    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise unauthorized

    if user.token_version != payload["token_version"]:
        raise unauthorized

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Allow access only to authenticated admin users."""

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return current_user


__all__ = [
    "get_db",
    "get_current_user",
    "get_current_admin",
]
