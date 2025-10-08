"""
Audit and performance tracking models
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class AdminAuditLog(BaseModel):
    """Admin audit log model"""
    __tablename__ = "admin_audit_log"
    
    admin_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(36), nullable=False)
    changes = Column(Text, nullable=True)  # JSON as text
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    
    # Relationships
    admin_user = relationship("User")
    
    def __repr__(self):
        return f"<AdminAuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type})>"


class TemplatePerformance(BaseModel):
    """Template performance tracking model"""
    __tablename__ = "template_performance"
    
    template_id = Column(String(36), ForeignKey("templates.id"), nullable=False)
    generation_request_id = Column(String(36), ForeignKey("generation_requests.id"), nullable=False)
    user_rating = Column(Integer, nullable=True)  # 1-5 scale
    processing_time = Column(DECIMAL(8,2), nullable=True)
    success = Column(Boolean, nullable=False)
    similarity_score = Column(DECIMAL(4,3), nullable=True)
    
    # Relationships
    template = relationship("Template", back_populates="performance_records")
    generation_request = relationship("GenerationRequest", back_populates="performance_record")
    
    def __repr__(self):
        return f"<TemplatePerformance(id={self.id}, success={self.success}, rating={self.user_rating})>"


class SystemSettings(BaseModel):
    """System settings model"""
    __tablename__ = "system_settings"
    
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)  # JSON as text
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<SystemSettings(id={self.id}, key={self.key}, is_public={self.is_public})>"