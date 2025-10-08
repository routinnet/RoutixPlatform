"""
Database models for Routix Platform
"""
from sqlalchemy.orm import relationship

from .base import BaseModel
from .user import User
from .template import Template
from .generation import GenerationAlgorithm, GenerationRequest
from .conversation import Conversation, Message
from .asset import UserAsset
from .transaction import CreditTransaction, Subscription
from .audit import AdminAuditLog, TemplatePerformance, SystemSettings

# Add missing relationships after imports
User.conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
User.generation_requests = relationship("GenerationRequest", back_populates="user", cascade="all, delete-orphan")
User.user_assets = relationship("UserAsset", back_populates="user", cascade="all, delete-orphan")
User.credit_transactions = relationship("CreditTransaction", back_populates="user", cascade="all, delete-orphan")
User.created_templates = relationship("Template", back_populates="created_by_user", cascade="all, delete-orphan")
User.subscription = relationship("Subscription", back_populates="user", uselist=False)

__all__ = [
    "BaseModel",
    "User",
    "Template",
    "GenerationAlgorithm",
    "GenerationRequest",
    "Conversation",
    "Message",
    "UserAsset",
    "CreditTransaction",
    "Subscription",
    "AdminAuditLog",
    "TemplatePerformance",
    "SystemSettings",
]