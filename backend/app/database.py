"""Async SQLAlchemy engine, session factory and request-scoped dependency.

Engine creation is lazy so process liveness and OpenAPI can be inspected even
when PostgreSQL or the async driver is not yet installed/configured. The
PostgreSQL readiness endpoint creates the engine on first real DB access.
"""
from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.models.base import Base


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Create the async PostgreSQL engine on first use."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.sqlalchemy_echo,
            pool_pre_ping=True,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout_seconds,
            connect_args={"timeout": settings.db_connect_timeout_seconds},
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the shared async session factory, creating it on first use."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped session; transaction ownership stays in services."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def dispose_database() -> None:
    """Close pooled database connections during application shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


__all__ = [
    "Base",
    "dispose_database",
    "get_db",
    "get_engine",
    "get_session_factory",
]
