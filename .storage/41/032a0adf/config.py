"""
Core configuration for Routix Platform
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Routix Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./routix.db"
    # For production: "postgresql+asyncpg://user:password@localhost/routix"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    MIDJOURNEY_API_KEY: Optional[str] = None
    
    # Storage
    CLOUDFLARE_R2_ACCESS_KEY: Optional[str] = None
    CLOUDFLARE_R2_SECRET_KEY: Optional[str] = None
    CLOUDFLARE_R2_BUCKET: str = "routix-storage"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"


settings = Settings()