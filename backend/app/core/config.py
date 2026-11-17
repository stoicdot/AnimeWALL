"""Typed application settings loaded from environment variables."""
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration; secrets are never stored in source code."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )
    # JWT authentication
    jwt_secret_key: SecretStr | None = None
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_access_token_expire_minutes: int = Field(
        default=15,
        ge=1,
        le=60,
    )
        # Supabase Storage
    supabase_url: str | None = None
    supabase_service_role_key: SecretStr | None = None
    supabase_storage_bucket: str = "animewall"

    app_name: str = "AnimeWall API"
    app_version: str = "0.1.0"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    api_prefix: str = "/api"

    # Required deliberately: developers must configure their own database URL.
    database_url: str = Field(min_length=1)
    db_pool_size: int = Field(default=5, ge=1, le=50)
    db_max_overflow: int = Field(default=10, ge=0, le=100)
    db_pool_timeout_seconds: int = Field(default=30, ge=1, le=300)
    db_connect_timeout_seconds: int = Field(default=5, ge=1, le=60)
    sqlalchemy_echo: bool = False

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:5500",
            "http://localhost:5500",
            "http://127.0.0.1:5501",
            "http://localhost:5501",
        ]
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Require PostgreSQL and normalize standard URLs to asyncpg URLs."""
        normalized = value.strip()
        if normalized.startswith("postgres://"):
            normalized = "postgresql+asyncpg://" + normalized.removeprefix("postgres://")
        elif normalized.startswith("postgresql://"):
            normalized = "postgresql+asyncpg://" + normalized.removeprefix("postgresql://")

        if not normalized.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use PostgreSQL with the asyncpg driver.")
        return normalized

    @field_validator("api_prefix")
    @classmethod
    def normalize_api_prefix(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith("/"):
            value = f"/{value}"
        return value.rstrip("/") or "/api"
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return one cached settings instance for the process."""
    return Settings()


settings = get_settings()
