"""
User assets and related models
"""
from sqlalchemy import Column, String, Integer, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class UserAsset(BaseModel):
    """User asset model"""
    __tablename__ = "user_assets"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    asset_type = Column(String(50), nullable=False)  # face_image, logo_image, custom_image
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_assets")
    
    def __repr__(self):
        return f"<UserAsset(id={self.id}, type={self.asset_type}, file_name={self.file_name})>"