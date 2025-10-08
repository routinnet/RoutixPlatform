"""
Base model with common fields
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
from app.core.database import Base


class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())