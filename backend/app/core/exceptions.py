"""Consistent API error responses without leaking internal exception details."""
import logging
from http import HTTPStatus
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class APIError(Exception):
    """An intentional, safe-to-display application error."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def error_body(
    request: Request,
    code: str,
    message: str,
    details: Any = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "request_id": getattr(request.state, "request_id", None),
        }
    }


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(request, exc.code, exc.message, exc.details),
    )


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    try:
        message = HTTPStatus(exc.status_code).phrase
    except ValueError:
        message = "Request failed."
    code = f"HTTP_{exc.status_code}"
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(request, code, message),
        headers=exc.headers,
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    # Exclude Pydantic's `input` and `ctx` values to avoid echoing submitted secrets.
    details = [
        {
            "field": ".".join(str(part) for part in item.get("loc", ())),
            "message": item.get("msg", "Invalid value."),
            "code": item.get("type", "validation_error"),
        }
        for item in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=error_body(
            request,
            "VALIDATION_ERROR",
            "One or more fields are invalid.",
            details,
        ),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("Unhandled request error; request_id=%s", request_id)
    return JSONResponse(
        status_code=500,
        content=error_body(
            request,
            "INTERNAL_SERVER_ERROR",
            "An unexpected server error occurred.",
        ),
    )
