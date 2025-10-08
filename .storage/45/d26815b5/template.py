"""
Template model
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, DECIMAL, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from .base import BaseModel


class Template(BaseModel):
    """Template model with vector embeddings"""
    __tablename__ = "templates"
    
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=False)
    style_dna = Column(JSON, nullable=True)  # JSONB in PostgreSQL
    # embedding = Column(Vector(1536), nullable=True)  # Will be added when using PostgreSQL
    category = Column(String(100), nullable=False, index=True)
    tags = Column(ARRAY(String), default=[], nullable=False)
    description = Column(Text, nullable=True)
    has_face = Column(Boolean, default=False, nullable=False)
    has_text = Column(Boolean, default=False, nullable=False)
    has_logo = Column(Boolean, default=False, nullable=False)
    energy_level = Column(Integer, nullable=True)  # 1-10 scale
    performance_score = Column(DECIMAL(4,2), default=5.0, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    success_rate = Column(DECIMAL(4,2), default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    created_by_user = relationship("User", back_populates="created_templates")
    generation_requests = relationship("GenerationRequest", back_populates="selected_template")
    performance_records = relationship("TemplatePerformance", back_populates="template", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Template(id={self.id}, category={self.category}, performance_score={self.performance_score})>"