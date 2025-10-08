"""
Routix Platform API Router
Main API router that includes all endpoint modules
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    templates,
    algorithms,
    generations,
    conversations,
    admin,
    websocket
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(algorithms.router, prefix="/algorithms", tags=["algorithms"])
api_router.include_router(generations.router, prefix="/generations", tags=["generations"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])