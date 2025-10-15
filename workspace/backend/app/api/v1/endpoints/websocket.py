"""
WebSocket Endpoints with Socket.IO
Real-time communication for generation progress and chat
"""

from typing import Any, Dict
import logging
from fastapi import APIRouter, Request
import socketio

# Create Socket.IO async server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Create ASGI app for Socket.IO
socket_app = socketio.ASGIApp(sio)

router = APIRouter()

# Store active connections
active_connections: Dict[str, Dict[str, Any]] = {}

logger = logging.getLogger(__name__)


@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    
    # Extract token from auth data
    token = None
    if auth and isinstance(auth, dict):
        token = auth.get('token')
    
    # Store connection info
    active_connections[sid] = {
        'token': token,
        'connected_at': '',
        'subscriptions': set()
    }
    
    await sio.emit('connection:established', {'connected': True}, room=sid)
    logger.info(f"✅ Connection established for {sid}")


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")
    
    # Clean up connection data
    if sid in active_connections:
        del active_connections[sid]
    
    logger.info(f"❌ Connection cleaned up for {sid}")


@sio.event
async def subscribe_generation(sid, data):
    """Subscribe to generation updates"""
    try:
        generation_id = data.get('generation_id')
        
        if not generation_id:
            await sio.emit('error', {'message': 'generation_id is required'}, room=sid)
            return
        
        # Add to subscriptions
        if sid in active_connections:
            active_connections[sid]['subscriptions'].add(generation_id)
        
        logger.info(f"Client {sid} subscribed to generation {generation_id}")
        
        # Send confirmation
        await sio.emit('subscribed', {
            'generation_id': generation_id,
            'status': 'subscribed'
        }, room=sid)
        
    except Exception as e:
        logger.error(f"Error subscribing to generation: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)


@sio.event
async def unsubscribe_generation(sid, data):
    """Unsubscribe from generation updates"""
    try:
        generation_id = data.get('generation_id')
        
        if not generation_id:
            await sio.emit('error', {'message': 'generation_id is required'}, room=sid)
            return
        
        # Remove from subscriptions
        if sid in active_connections:
            active_connections[sid]['subscriptions'].discard(generation_id)
        
        logger.info(f"Client {sid} unsubscribed from generation {generation_id}")
        
        # Send confirmation
        await sio.emit('unsubscribed', {
            'generation_id': generation_id,
            'status': 'unsubscribed'
        }, room=sid)
        
    except Exception as e:
        logger.error(f"Error unsubscribing from generation: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)


# Helper functions to emit generation events
async def emit_generation_started(generation_id: str, data: Dict[str, Any]):
    """Emit generation started event to all subscribers"""
    try:
        # Find all subscribers
        for sid, conn_data in active_connections.items():
            if generation_id in conn_data['subscriptions']:
                await sio.emit('generation_started', {
                    'generation_id': generation_id,
                    'status': 'processing',
                    'progress': 0,
                    **data
                }, room=sid)
                
        logger.info(f"📢 Emitted generation_started for {generation_id}")
    except Exception as e:
        logger.error(f"Error emitting generation_started: {e}")


async def emit_generation_progress(generation_id: str, data: Dict[str, Any]):
    """Emit generation progress event to all subscribers"""
    try:
        # Find all subscribers
        for sid, conn_data in active_connections.items():
            if generation_id in conn_data['subscriptions']:
                await sio.emit('generation_progress', {
                    'generation_id': generation_id,
                    'status': 'processing',
                    **data
                }, room=sid)
                
        logger.info(f"📊 Emitted generation_progress for {generation_id}: {data.get('progress', 0)}%")
    except Exception as e:
        logger.error(f"Error emitting generation_progress: {e}")


async def emit_generation_completed(generation_id: str, data: Dict[str, Any]):
    """Emit generation completed event to all subscribers"""
    try:
        # Find all subscribers
        for sid, conn_data in active_connections.items():
            if generation_id in conn_data['subscriptions']:
                await sio.emit('generation_completed', {
                    'generation_id': generation_id,
                    'status': 'completed',
                    'progress': 100,
                    **data
                }, room=sid)
                
        logger.info(f"✅ Emitted generation_completed for {generation_id}")
    except Exception as e:
        logger.error(f"Error emitting generation_completed: {e}")


async def emit_generation_failed(generation_id: str, data: Dict[str, Any]):
    """Emit generation failed event to all subscribers"""
    try:
        # Find all subscribers
        for sid, conn_data in active_connections.items():
            if generation_id in conn_data['subscriptions']:
                await sio.emit('generation_failed', {
                    'generation_id': generation_id,
                    'status': 'failed',
                    **data
                }, room=sid)
                
        logger.error(f"❌ Emitted generation_failed for {generation_id}")
    except Exception as e:
        logger.error(f"Error emitting generation_failed: {e}")


async def emit_queue_position(generation_id: str, data: Dict[str, Any]):
    """Emit queue position update to all subscribers"""
    try:
        # Find all subscribers
        for sid, conn_data in active_connections.items():
            if generation_id in conn_data['subscriptions']:
                await sio.emit('queue_position', {
                    'generation_id': generation_id,
                    **data
                }, room=sid)
                
        logger.info(f"📍 Emitted queue_position for {generation_id}: position {data.get('queue_position', 0)}")
    except Exception as e:
        logger.error(f"Error emitting queue_position: {e}")


# Legacy WebSocket endpoint (for backward compatibility)
@router.websocket("/generation-progress")
async def websocket_generation_progress(websocket):
    """Legacy WebSocket endpoint - use Socket.IO instead"""
    from fastapi import WebSocket, WebSocketDisconnect
    
    if isinstance(websocket, WebSocket):
        await websocket.accept()
        
        await websocket.send_json({
            "type": "info",
            "message": "This endpoint is deprecated. Please use Socket.IO connection instead."
        })
        
        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_json({
                    "type": "echo",
                    "data": data,
                    "message": "Use Socket.IO for real-time updates"
                })
        except WebSocketDisconnect:
            pass