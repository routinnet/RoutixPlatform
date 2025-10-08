"""Configuration settings for the Routix Platform backend."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, Field, model_validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "routix.db"
DEFAULT_DB_URL = f"sqlite+aiosqlite:///{DEFAULT_DB_PATH.as_posix()}"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Basic app settings
    PROJECT_NAME: str = "Routix Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database
    DATABASE_URL: str = DEFAULT_DB_URL

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Services
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Networking / CORS
    BACKEND_CORS_ORIGINS: List[Union[AnyHttpUrl, str]] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    ALLOWED_HOSTS: List[str] = Field(default_factory=lambda: ["*"])

    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(
        default_factory=lambda: [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
        ]
    )

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Embedding settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536
    EMBEDDING_CACHE_TTL: int = 86_400  # 24 hours
    EMBEDDING_BATCH_SIZE: int = 100

    @property
    def is_production(self) -> bool:
        """Return True when the application runs in production mode."""

        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_debug(self) -> bool:
        """Expose the debug flag via a semantic helper property."""

        return bool(self.DEBUG)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def expand_sqlite_path(cls, value: str) -> str:
        """Ensure SQLite URLs always resolve to an absolute path on disk."""

        if not isinstance(value, str):
            return value

        if value.startswith("sqlite+aiosqlite:///"):
            path_fragment = value.replace("sqlite+aiosqlite:///", "", 1)
            db_path = Path(path_fragment)
            if not db_path.is_absolute():
                db_path = BASE_DIR / db_path
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{db_path.as_posix()}"
        return value

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, value: Union[str, List[Union[str, AnyHttpUrl]], None]
    ) -> List[str]:
        """Normalise the list of allowed CORS origins."""

        if not value:
            return []
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, str):
            # FastAPI's env loader may provide JSON-style lists as plain strings; parse
            # them eagerly so the CORS middleware receives each origin separately.
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
                raise ValueError("Invalid JSON for BACKEND_CORS_ORIGINS") from exc
            return [str(origin).strip() for origin in parsed if str(origin).strip()]
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        raise ValueError(value)

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(
        cls, value: Union[str, List[str], None]
    ) -> List[str]:
        """Normalise the list of allowed hosts for trusted host middleware."""

        if not value:
            return ["*"]
        if isinstance(value, str) and not value.startswith("["):
            return [host.strip() for host in value.split(",") if host.strip()]
        if isinstance(value, str):
            # Mirror the CORS parser so JSON-style lists in env vars expand correctly.
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
                raise ValueError("Invalid JSON for ALLOWED_HOSTS") from exc
            return [str(host).strip() for host in parsed if str(host).strip()]
        if isinstance(value, list):
            return [str(host).strip() for host in value if str(host).strip()]
        raise ValueError(value)

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        """Fail fast when a production deployment uses the placeholder secret."""

        if self.is_production and self.SECRET_KEY.startswith("your-secret-key"):
            raise ValueError(
                "SECRET_KEY must be set to a secure value in production deployments."
            )
        return self


settings = Settings()

__all__ = ["settings", "Settings"]
