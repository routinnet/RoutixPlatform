"""
Routix Platform Configuration
Environment variables and application settings
"""

import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Basic app settings
    PROJECT_NAME: str = "Routix Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:8000",
        "https://routix.dev",
        "https://app.routix.dev"
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Allowed hosts
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "routix.dev", "*.routix.dev"]
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "routix_user"
    POSTGRES_PASSWORD: str = "routix_password"
    POSTGRES_DB: str = "routix_db"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    
    # AI Services
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    MIDJOURNEY_API_KEY: str = ""
    MIDJOURNEY_API_URL: str = "https://api.useapi.net/v2/jobs"
    
    # File Storage
    STORAGE_TYPE: str = "local"  # local, s3, cloudflare_r2
    UPLOAD_DIR: str = "/tmp/routix_uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
    
    # AWS S3 / Cloudflare R2
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "routix-thumbnails"
    
    # Stripe
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    GENERATION_RATE_LIMIT: int = 10  # generations per minute
    
    # WebSocket
    WS_MAX_CONNECTIONS: int = 1000
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Global settings instance
settings = Settings()