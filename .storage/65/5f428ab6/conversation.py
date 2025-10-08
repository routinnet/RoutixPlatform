"""
Conversation and message models
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from .base import BaseModel


class Conversation(BaseModel):
    """Conversation model"""
    __tablename__ = "conversations"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    generation_requests = relationship("GenerationRequest", back_populates="conversation")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title}, message_count={self.message_count})>"


class Message(BaseModel):
    """Message model"""
    __tablename__ = "messages"
    
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    type = Column(String(50), nullable=False)  # text, thumbnail_result, progress_update, etc.
    content = Column(Text, nullable=False)
    message_metadata = Column(Text, default='{}', nullable=False)  # JSON as text - renamed to avoid conflict
    timestamp = Column(DateTime(timezone=True), nullable=False)
    is_edited = Column(Boolean, default=False, nullable=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, type={self.type})>"