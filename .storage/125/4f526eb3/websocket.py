"""
WebSocket Endpoints
Real-time communication for generation progress
"""

from typing import Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db

router = APIRouter()


@router.websocket("/generation-progress")
async def websocket_generation_progress(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket for real-time generation progress (placeholder)"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass