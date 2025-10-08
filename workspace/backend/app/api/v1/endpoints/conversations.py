"""
Conversation Endpoints
Chat history, messages
"""

from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get user conversations (placeholder)"""
    return {"message": "Conversations endpoint - coming soon"}


@router.post("/")
async def create_conversation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create conversation (placeholder)"""
    return {"message": "Create conversation endpoint - coming soon"}