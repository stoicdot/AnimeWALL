"""AnimeWall FastAPI application entry point."""
from contextlib import asynccontextmanager
import logging
from app.routers.health import router as health_router
from app.routers.categories import router as categories_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import (
    APIError,
    api_error_handler,
    http_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from app.core.middleware import RequestIDMiddleware
from app.database import dispose_database
from app.routers.health import router as health_router
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError


logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Release database connections when Uvicorn shuts down.

    The app intentionally does not fail startup when PostgreSQL is down;
    orchestration can use /api/health/ready to detect that condition.
    """
    yield
    await dispose_database()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for AnimeWall — Find Your Anime Aesthetic.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

# CORS is restricted to configured frontend origins; credentials never use wildcard origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(RequestIDMiddleware)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(categories_router, prefix=settings.api_prefix)

@app.get("/", tags=["System"], include_in_schema=False)
async def root() -> dict[str, object]:
    return {
        "data": {
            "service": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": f"{settings.api_prefix}/health/live",
        }
    }
