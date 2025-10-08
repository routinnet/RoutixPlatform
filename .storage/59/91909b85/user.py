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
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, credits={self.credits})>"