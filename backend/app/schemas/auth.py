
"""Request and response schemas for AnimeWall authentication."""

from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
)


class RegisterRequest(BaseModel):
    """Data required to register a new account."""

    username: str = Field(
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_]+$",
    )

    email: EmailStr

    password: SecretStr = Field(
        min_length=12,
        max_length=128,
    )


class LoginRequest(BaseModel):
    """Credentials required to log in."""

    email: EmailStr

    password: SecretStr = Field(
        min_length=1,
        max_length=128,
    )


class AuthUser(BaseModel):
    """Public user information returned after authentication."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    role: Literal["user", "admin"]


class AuthTokenData(BaseModel):
    """Access token and authenticated user information."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: AuthUser


class AuthResponse(BaseModel):
    """Standard authentication response envelope."""

    data: AuthTokenData
class AuthUserResponse(BaseModel):
    """Response containing the authenticated user's details."""

    data: AuthUser