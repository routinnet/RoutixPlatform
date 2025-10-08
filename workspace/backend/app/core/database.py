"""Database configuration and session management utilities."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Dict

from sqlalchemy import MetaData
from sqlalchemy.engine import URL
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings

SqliteConnectArgs = Dict[str, object]


def _build_engine() -> AsyncEngine:
    """Instantiate the SQLAlchemy async engine configured for the application."""

    database_url: URL = make_url(settings.DATABASE_URL)
    connect_args: SqliteConnectArgs = {}

    if database_url.get_backend_name().startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.is_debug,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


# Database engine
engine = _build_engine()


# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base class for models
class Base(DeclarativeBase):
    """Base declarative class used across all ORM models."""

    metadata = MetaData()


@asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Provide a managed async database session with automatic rollback on error."""

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency for retrieving an async session."""

    async with get_db_session() as session:
        yield session


__all__ = ["AsyncSessionLocal", "Base", "engine", "get_db", "get_db_session"]
