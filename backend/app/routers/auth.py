
"""Authentication endpoints for AnimeWall."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import AuthUserResponse, AuthUser

from app.core.config import settings
from app.database import get_db
from app.schemas.auth import (
    AuthResponse,
    AuthTokenData,
    AuthUser,
    LoginRequest,
    RegisterRequest,
)
from app.services.auth import authenticate_user, register_user
from app.services.tokens import create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new AnimeWall account",
)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Create a user account and return an access token."""

    user = await register_user(
        session,
        username=payload.username,
        email=str(payload.email),
        password=payload.password.get_secret_value(),
    )

    access_token = create_access_token(
        subject=user.id,
        token_version=user.token_version,
    )

    return AuthResponse(
        data=AuthTokenData(
            access_token=access_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user=AuthUser.model_validate(user),
        )
    )

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Log in to an AnimeWall account",
)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Authenticate user and return an access token."""

    user = await authenticate_user(
        session,
        email=str(payload.email),
        password=payload.password.get_secret_value(),
    )

    access_token = create_access_token(
        subject=user.id,
        token_version=user.token_version,
    )

    return AuthResponse(
        data=AuthTokenData(
            access_token=access_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user=AuthUser.model_validate(user),
        )
    )

@router.get(
    "/me",
    response_model=AuthUserResponse,
    status_code=200,
)
async def read_current_user(
    current_user: User = Depends(get_current_user),
) -> AuthUserResponse:

    user_data = AuthUser.model_validate(
        current_user,
        from_attributes=True
    )

    return AuthUserResponse(data=user_data)