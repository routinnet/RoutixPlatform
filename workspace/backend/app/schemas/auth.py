"""
Authentication Schemas
Pydantic models for authentication endpoints
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    full_name: str
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
    
    @validator("full_name")
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        return v.strip()


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset with token"""
    token: str
    new_password: str
    
    @validator("new_password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: Optional[str] = None
    exp: Optional[int] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = False