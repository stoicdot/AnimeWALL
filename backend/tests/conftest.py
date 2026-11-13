"""Test configuration; the test database URL is never used for real queries."""
import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test_user:test_password@127.0.0.1:5432/test_animewall",
)
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("CORS_ORIGINS", '["http://localhost"]')
