"""
Generation-related models
"""
from sqlalchemy import Column, String, Text, Integer, DECIMAL, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class GenerationAlgorithm(BaseModel):
    """Generation algorithm model"""
    __tablename__ = "generation_algorithms"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    ai_provider = Column(String(50), nullable=False)  # midjourney, dalle3, sdxl, etc.
    config = Column(Text, nullable=True)  # JSON config as text for SQLite compatibility
    cost_per_generation = Column(DECIMAL(10,4), nullable=False)
    credit_cost = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    performance_metrics = Column(Text, default='{}', nullable=False)  # JSON as text
    
    # Relationships
    generation_requests = relationship("GenerationRequest", back_populates="algorithm")
    
    def __repr__(self):
        return f"<GenerationAlgorithm(id={self.id}, name={self.name}, provider={self.ai_provider})>"


class GenerationRequest(BaseModel):
    """Generation request model"""
    __tablename__ = "generation_requests"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=True)
    algorithm_id = Column(String(36), ForeignKey("generation_algorithms.id"), nullable=False)
    selected_template_id = Column(String(36), ForeignKey("templates.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    enhanced_prompt = Column(Text, nullable=True)
    user_face_url = Column(String(500), nullable=True)
    user_logo_url = Column(String(500), nullable=True)
    custom_text = Column(String(500), nullable=True)
    status = Column(String(50), default='pending', nullable=False)
    progress = Column(Integer, default=0, nullable=False)
    final_thumbnail_url = Column(String(500), nullable=True)
    processing_time = Column(DECIMAL(8,2), nullable=True)
    cost_incurred = Column(DECIMAL(10,4), default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="generation_requests")
    conversation = relationship("Conversation", back_populates="generation_requests")
    algorithm = relationship("GenerationAlgorithm", back_populates="generation_requests")
    selected_template = relationship("Template", back_populates="generation_requests")
    credit_transactions = relationship("CreditTransaction", back_populates="generation_request")
    performance_record = relationship("TemplatePerformance", back_populates="generation_request", uselist=False)
    
    def __repr__(self):
        return f"<GenerationRequest(id={self.id}, status={self.status}, progress={self.progress})>"