"""Liveness and readiness endpoints for local development and deployment checks."""
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import error_body
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", summary="Check whether the API process is alive")
async def liveness() -> dict[str, object]:
    """Liveness does not depend on PostgreSQL availability."""
    return {
        "data": {
            "status": "alive",
            "service": settings.app_name,
            "version": settings.app_version,
        }
    }


@router.get("/ready", summary="Check whether the API can reach PostgreSQL")
async def readiness(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Readiness runs a minimal database query and returns no connection details."""
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.warning(
            "Database readiness check failed; request_id=%s exception_type=%s",
            getattr(request.state, "request_id", "unknown"),
            type(exc).__name__,
        )
        return JSONResponse(
            status_code=503,
            content=error_body(
                request,
                "DATABASE_UNAVAILABLE",
                "The service is temporarily unavailable.",
            ),
        )

    return {
        "data": {
            "status": "ready",
            "database": "connected",
            "service": settings.app_name,
        }
    }
