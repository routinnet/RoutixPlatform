"""
Routix Platform - Main FastAPI Application
AI-powered thumbnail generation with chat interface
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.core.exceptions import RouxixException


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Routix Platform...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Create database tables (if needed)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Routix Platform started successfully!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Routix Platform...")
    await engine.dispose()
    logger.info("✅ Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Routix Platform API",
    description="AI-powered thumbnail generation with chat interface",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
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
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
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
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
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
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "routix-platform",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with database connectivity"""
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
            await db.execute("SELECT 1")
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
async def root():
    return {
        "message": "Welcome to Routix Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }