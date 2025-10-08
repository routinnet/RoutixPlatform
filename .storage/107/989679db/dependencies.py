"""
Routix Platform Dependencies
FastAPI dependency injection for database, authentication, etc.
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import jwt_bearer
from app.models.user import User
from app.services.user_service import UserService


async def get_db() -> AsyncSession:
    """Get database session dependency"""
    async with get_db_session() as session:
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(jwt_bearer)
) -> User:
    """Get current authenticated user"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user (alias for clarity)"""
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current admin user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(jwt_bearer)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not token:
        return None
    
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(token)
        
        if user and user.is_active:
            return user
    except Exception:
        pass
    
    return None


class CommonQueryParams:
    """Common query parameters for pagination and filtering"""
    
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ):
        self.skip = skip
        self.limit = min(limit, 1000)  # Max 1000 items per page
        self.search = search
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order.lower() in ["asc", "desc"] else "asc"


def get_query_params(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> CommonQueryParams:
    """Get common query parameters dependency"""
    return CommonQueryParams(skip, limit, search, sort_by, sort_order)


# Rate limiting dependency
async def rate_limit_dependency(request):
    """Rate limiting dependency"""
    from app.core.security import rate_limiter
    from app.core.config import settings
    
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(
        f"api:{client_ip}", 
        settings.RATE_LIMIT_PER_MINUTE
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )


# WebSocket authentication
async def websocket_auth(websocket, token: str):
    """Authenticate WebSocket connection"""
    from app.core.security import verify_token
    
    user_id = verify_token(token)
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return None
    
    return user_id