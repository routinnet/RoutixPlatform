"""
Authentication Endpoints
Login, register, token refresh, password reset
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password
)
from app.models.user import User
from app.schemas.auth import (
    Token,
    TokenRefresh,
    UserLogin,
    UserRegister,
    PasswordReset,
    PasswordResetRequest
)
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user"""
    user_service = UserService(db)
    
    # Check if user already exists
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = await user_service.create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Login with email and password"""
    user_service = UserService(db)
    
    # Authenticate user
    user = await user_service.authenticate_user(
        email=form_data.username,  # OAuth2 uses 'username' field
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={"email": user.email, "is_admin": user.is_admin}
    )
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/login/json", response_model=Token)
async def login_json(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Login with JSON payload"""
    user_service = UserService(db)
    
    # Authenticate user
    user = await user_service.authenticate_user(
        email=user_data.email,
        password=user_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={"email": user.email, "is_admin": user.is_admin}
    )
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token"""
    user_id = verify_token(token_data.refresh_token, token_type="refresh")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={"email": user.email, "is_admin": user.is_admin}
    )
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/password-reset-request")
async def password_reset_request(
    request_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Request password reset"""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_email(request_data.email)
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset link has been sent"}
    
    # In a real app, you would send an email with the reset token
    # For now, we'll just return success
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset")
async def password_reset(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Reset password with token"""
    from app.core.security import verify_password_reset_token
    
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    await user_service.update_user_password(user.id, reset_data.new_password)
    
    return {"message": "Password updated successfully"}


@router.post("/logout")
async def logout() -> Any:
    """Logout (client should discard tokens)"""
    return {"message": "Successfully logged out"}