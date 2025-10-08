"""
Database models for Routix Platform
"""
from .base import BaseModel
from .user import User
from .template import Template
from .generation import GenerationAlgorithm, GenerationRequest
from .conversation import Conversation, Message
from .asset import UserAsset
from .transaction import CreditTransaction, Subscription
from .audit import AdminAuditLog, TemplatePerformance, SystemSettings

# Add missing relationships
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