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
    generation,
    chat,
    admin,
    websocket
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(algorithms.router, prefix="/algorithms", tags=["algorithms"])
api_router.include_router(generation.router, prefix="/generation", tags=["generation"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])