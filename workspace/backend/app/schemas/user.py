"""
User schemas for Routix Platform
"""
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False

class User(UserBase):
    id: str
    credits: int = 0
    
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    credits: Optional[int] = None

class UserInDB(User):
    hashed_password: str