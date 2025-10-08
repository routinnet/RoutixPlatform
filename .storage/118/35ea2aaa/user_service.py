"""
User Service
Business logic for user management
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import NotFoundError, ConflictError


class UserService:
    """Service for user-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            uuid_id = UUID(user_id)
        except ValueError:
            return None
            
        result = await self.db.execute(
            select(User).where(User.id == uuid_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        is_admin: bool = False
    ) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ConflictError(f"User with email {email} already exists")
        
        # Create new user
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_admin=is_admin,
            credits=10  # Free tier credits
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def update_user_password(self, user_id: UUID, new_password: str) -> User:
        """Update user password"""
        user = await self.get_user_by_id(str(user_id))
        if not user:
            raise NotFoundError("User", str(user_id))
        
        user.hashed_password = get_password_hash(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_user_credits(self, user_id: UUID, credits: int) -> User:
        """Update user credits"""
        user = await self.get_user_by_id(str(user_id))
        if not user:
            raise NotFoundError("User", str(user_id))
        
        user.credits = credits
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def deduct_credits(self, user_id: UUID, amount: int) -> User:
        """Deduct credits from user"""
        user = await self.get_user_by_id(str(user_id))
        if not user:
            raise NotFoundError("User", str(user_id))
        
        if user.credits < amount:
            from app.core.exceptions import InsufficientCreditsError
            raise InsufficientCreditsError(amount, user.credits)
        
        user.credits -= amount
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[User]:
        """Get list of users with pagination"""
        query = select(User)
        
        if search:
            query = query.where(
                User.email.ilike(f"%{search}%") |
                User.full_name.ilike(f"%{search}%")
            )
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user"""
        user = await self.get_user_by_id(str(user_id))
        if not user:
            raise NotFoundError("User", str(user_id))
        
        await self.db.delete(user)
        await self.db.commit()
        
        return True