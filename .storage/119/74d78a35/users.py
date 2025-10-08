"""
User Management Endpoints
User profile, settings, credits
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_db,
    get_current_user,
    get_current_admin_user,
    get_query_params,
    CommonQueryParams
)
from app.models.user import User
from app.schemas.user import UserResponse, UserProfile, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update current user profile"""
    user_service = UserService(db)
    
    # Update user fields
    if user_update.email is not None:
        # Check if email is already taken
        existing_user = await user_service.get_user_by_email(user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/", response_model=List[UserResponse])
async def get_users(
    query_params: CommonQueryParams = Depends(get_query_params),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get list of users (admin only)"""
    user_service = UserService(db)
    
    users = await user_service.get_users(
        skip=query_params.skip,
        limit=query_params.limit,
        search=query_params.search
    )
    
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get user by ID (admin only)"""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete user (admin only)"""
    user_service = UserService(db)
    
    await user_service.delete_user(user_id)
    
    return {"message": "User deleted successfully"}