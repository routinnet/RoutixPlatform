"""
User model
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    """User model"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    credits = Column(Integer, default=10, nullable=False)
    subscription_tier = Column(String(50), default='free', nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    generation_requests = relationship("GenerationRequest", back_populates="user", cascade="all, delete-orphan")
    user_assets = relationship("UserAsset", back_populates="user", cascade="all, delete-orphan")
    credit_transactions = relationship("CreditTransaction", back_populates="user", cascade="all, delete-orphan")
    created_templates = relationship("Template", back_populates="created_by_user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, credits={self.credits})>"