"""
Admin Panel Endpoints
Dashboard, analytics, system management
"""

from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get admin dashboard data (placeholder)"""
    return {"message": "Admin dashboard endpoint - coming soon"}


@router.get("/stats")
async def get_system_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get system statistics (placeholder)"""
    return {"message": "System stats endpoint - coming soon"}