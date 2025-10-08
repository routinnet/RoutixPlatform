"""Routix Platform FastAPI application entrypoint."""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.api.v1.api import api_router
from app.core.exceptions import RouxixException


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Run start-up and shutdown routines for the FastAPI app."""

    logger.info("🚀 Starting Routix Platform…")
    logger.info("Environment: %s", settings.ENVIRONMENT)
    logger.info("Debug mode: %s", settings.is_debug)

    # This is intentionally commented until database migrations are introduced.
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    logger.info("✅ Routix Platform started successfully!")

    try:
        yield
    finally:
        logger.info("🛑 Shutting down Routix Platform…")
        await engine.dispose()
        logger.info("✅ Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Routix Platform API",
    description="AI-powered thumbnail generation with chat interface",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.is_debug else None,
    docs_url="/docs" if settings.is_debug else None,
    redoc_url="/redoc" if settings.is_debug else None,
    lifespan=lifespan
)


# Security middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Annotate responses with their processing duration."""

    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    return response


# Exception handlers
@app.exception_handler(RouxixException)
async def routix_exception_handler(request: Request, exc: RouxixException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Fallback handler for uncaught exceptions."""

    logger.exception("Unhandled exception during request")
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred"
        }
    )


# Health check endpoints
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "routix-platform",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with database connectivity."""
    from app.core.database import get_db_session
    
    health_status = {
        "status": "healthy",
        "service": "routix-platform",
        "version": "1.0.0",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Database check
    try:
        async with get_db_session() as db:
            # SQLAlchemy 2.0 requires textual SQL to be wrapped in text() to avoid
            # ArgumentError in async contexts, so the health check always succeeds.
            await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    return health_status


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """Return a friendly landing payload for the API root."""

    return {
        "message": "Welcome to Routix Platform API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.is_debug else None,
        "health": "/health",
    }
