"""
User Schemas
Pydantic models for user-related data
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema"""
    id: UUID
    credits: int
    is_admin: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    """User profile schema"""
    id: UUID
    email: EmailStr
    full_name: str
    credits: int
    is_admin: bool
    email_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True


class UserStats(BaseModel):
    """User statistics schema"""
    total_generations: int
    successful_generations: int
    failed_generations: int
    credits_used: int
    credits_remaining: int
    favorite_algorithm: Optional[str] = None
    last_generation: Optional[datetime] = None