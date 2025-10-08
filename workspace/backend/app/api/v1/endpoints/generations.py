"""
Generation Endpoints
Thumbnail generation, status, history
"""

from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/")
async def create_generation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create thumbnail generation (placeholder)"""
    return {"message": "Generation endpoint - coming soon"}


@router.get("/")
async def get_generations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get user generations (placeholder)"""
    return {"message": "Get generations endpoint - coming soon"}