"""
Transaction and subscription models
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class CreditTransaction(BaseModel):
    """Credit transaction model"""
    __tablename__ = "credit_transactions"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    generation_request_id = Column(String(36), ForeignKey("generation_requests.id"), nullable=True)
    transaction_type = Column(String(50), nullable=False)  # purchase, generation_cost, refund, bonus, subscription_credit
    amount = Column(Integer, nullable=False)  # Can be negative for costs
    balance_after = Column(Integer, nullable=False)
    description = Column(String(255), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="credit_transactions")
    generation_request = relationship("GenerationRequest", back_populates="credit_transactions")
    
    def __repr__(self):
        return f"<CreditTransaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"


class Subscription(BaseModel):
    """Subscription model"""
    __tablename__ = "subscriptions"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    plan_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # active, cancelled, past_due, unpaid, incomplete
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="subscription", uselist=False)
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, plan={self.plan_name}, status={self.status})>"