"""FastAPI application entrypoint."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import (
    categories_router,
    orders_router,
    products_router,
    reports_router,
)
from app.core.config import get_settings
from app.core.database import check_database_connection
from app.core.exceptions import AppError, ServiceUnavailableError


logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(reports_router)


@app.exception_handler(AppError)
async def app_error_handler(_, exc: AppError) -> JSONResponse:
    """Serialize application exceptions into stable JSON responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception) -> JSONResponse:
    """Return a generic error response for unhandled exceptions."""
    logger.exception("Unhandled application error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "internal_server_error",
        },
    )


@app.get("/", tags=["meta"])
def read_root() -> dict[str, str]:
    """Return basic application metadata."""
    return {
        "application": settings.app_name,
        "environment": settings.app_env,
        "status": "starting",
    }


@app.get("/health", tags=["meta"])
def health_check() -> dict[str, str]:
    """Return application and database health."""
    try:
        check_database_connection()
    except SQLAlchemyError as exc:
        raise ServiceUnavailableError("Database connectivity check failed") from exc

    return {
        "status": "ok",
        "application": "up",
        "database": "up",
    }
