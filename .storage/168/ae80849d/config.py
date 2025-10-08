"""
Configuration settings for Routix Platform
"""
import os
from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
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
    DATABASE_URL: str = "postgresql+asyncpg://routix:routix123@localhost/routix_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Services
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Load settings from environment
settings = Settings()

# Override with environment variables if they exist
if os.getenv("GEMINI_API_KEY"):
    settings.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if os.getenv("OPENAI_API_KEY"):
    settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if os.getenv("DATABASE_URL"):
    settings.DATABASE_URL = os.getenv("DATABASE_URL")

if os.getenv("REDIS_URL"):
    settings.REDIS_URL = os.getenv("REDIS_URL")

if os.getenv("SECRET_KEY"):
    settings.SECRET_KEY = os.getenv("SECRET_KEY")

if os.getenv("DEBUG"):
    settings.DEBUG = os.getenv("DEBUG").lower() == "true"

if os.getenv("ENVIRONMENT"):
    settings.ENVIRONMENT = os.getenv("ENVIRONMENT")