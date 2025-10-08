"""
Chat and conversation management endpoints
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from app.services.chat_service import chat_service, ChatServiceError, ConversationType, MessageType
from app.core.dependencies import get_current_user
from app.schemas.user import User

router = APIRouter()

class ConversationCreateRequest(BaseModel):
    title: Optional[str] = None
    conversation_type: ConversationType = ConversationType.GENERAL
    participants: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageSendRequest(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT
    reply_to: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

class TitleUpdateRequest(BaseModel):
    title: str

@router.post("/conversations", response_model=Dict[str, Any])
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new conversation
    """
    try:
        result = await chat_service.create_conversation(
            user_id=current_user.id,
            title=request.title,
            conversation_type=request.conversation_type,
            participants=request.participants,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Conversation created successfully"
        }
        
    except ChatServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")

@router.get("/conversations", response_model=Dict[str, Any])
async def get_conversations(
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Results offset for pagination"),
    conversation_type: Optional[ConversationType] = Query(None, description="Filter by conversation type"),
    search: Optional[str] = Query(None, description="Search conversations"),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's conversations with filtering and pagination
    """
    try:
        result = await chat_service.get_conversations(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            conversation_type=conversation_type,
            search_query=search
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Conversations retrieved successfully"
        }
        
    except ChatServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation(
    conversation_id: str,
    include_messages: bool = Query(True, description="Include messages in response"),
    message_limit: int = Query(50, ge=1, le=200, description="Maximum messages to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation details with messages
    """
    try:
        result = await chat_service.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id,
            include_messages=include_messages,
            message_limit=message_limit
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Conversation retrieved successfully"
        }
        
    except ChatServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")

@router.post("/conversations/{conversation_id}/messages", response_model=Dict[str, Any])
async def send_message(
    conversation_id: str,
    request: MessageSendRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to a conversation
    """
    try:
        result = await chat_service.send_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            content=request.content,
            message_type=request.message_type,
            reply_to=request.reply_to,
            attachments=request.attachments,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Message sent successfully"
        }
        
    except ChatServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.put("/conversations/{conversation_id}/title", response_model=Dict[str, Any])
async def update_conversation_title(
    conversation_id: str,
    request: TitleUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update conversation title
    """
    try:
        result = await chat_service.update_conversation_title(
            conversation_id=conversation_id,
            user_id=current_user.id,
            new_title=request.title
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Title updated successfully"
        }
        
    except ChatServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update title: {str(e)}")

@router.delete("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def delete_conversation(
    conversation_id: str,
    soft_delete: bool = Query(True, description="Whether to soft delete (true) or hard delete (false)"),
    current_user: User = Depends(get_current_user)
):
    """
    Delete conversation
    """
    try:
        result = await chat_service.delete_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id,
            soft_delete=soft_delete
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Conversation deleted successfully"
        }
        
    except ChatServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

@router.get("/search", response_model=Dict[str, Any])
async def search_conversations(
    query: str = Query(..., description="Search query"),
    conversation_id: Optional[str] = Query(None, description="Search within specific conversation"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Search within conversations and messages
    """
    try:
        result = await chat_service.search_conversations(
            user_id=current_user.id,
            query=query,
            conversation_id=conversation_id,
            limit=limit
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Search completed successfully"
        }
        
    except ChatServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/conversations/{conversation_id}/export", response_model=Dict[str, Any])
async def export_conversation(
    conversation_id: str,
    format: str = Query("json", regex="^(json|txt|pdf)$", description="Export format"),
    include_metadata: bool = Query(True, description="Include metadata in export"),
    current_user: User = Depends(get_current_user)
):
    """
    Export conversation to various formats
    """
    try:
        result = await chat_service.export_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id,
            format=format,
            include_metadata=include_metadata
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Export completed successfully"
        }
        
    except ChatServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/conversations/{conversation_id}/participants", response_model=Dict[str, Any])
async def get_conversation_participants(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation participants
    """
    try:
        # Get conversation data to check participants
        conversation_data = await chat_service.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id,
            include_messages=False
        )
        
        participants = conversation_data.get("participants", [])
        
        # Mock participant details (replace with actual user service)
        participant_details = []
        for participant_id in participants:
            participant_details.append({
                "user_id": participant_id,
                "username": f"user_{participant_id}",
                "is_online": True,  # Mock status
                "last_seen": "2024-10-07T12:00:00Z"
            })
        
        return {
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "participants": participant_details,
                "total_participants": len(participant_details)
            },
            "message": "Participants retrieved successfully"
        }
        
    except ChatServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get participants: {str(e)}")

@router.post("/conversations/{conversation_id}/participants", response_model=Dict[str, Any])
async def add_participant(
    conversation_id: str,
    participant_id: str = Query(..., description="User ID to add to conversation"),
    current_user: User = Depends(get_current_user)
):
    """
    Add participant to conversation
    """
    try:
        # Get conversation data
        conversation_data = await chat_service.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id,
            include_messages=False
        )
        
        # Check if user is creator or admin
        if conversation_data.get("creator_id") != current_user.id:
            raise HTTPException(status_code=403, detail="Only conversation creator can add participants")
        
        # Add participant (mock implementation)
        participants = conversation_data.get("participants", [])
        if participant_id not in participants:
            participants.append(participant_id)
            
            # Update conversation (mock)
            # In production, update database
            
            return {
                "success": True,
                "data": {
                    "conversation_id": conversation_id,
                    "added_participant": participant_id,
                    "total_participants": len(participants)
                },
                "message": "Participant added successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="User is already a participant")
        
    except ChatServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add participant: {str(e)}")

@router.delete("/conversations/{conversation_id}/participants/{participant_id}", response_model=Dict[str, Any])
async def remove_participant(
    conversation_id: str,
    participant_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove participant from conversation
    """
    try:
        # Get conversation data
        conversation_data = await chat_service.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id,
            include_messages=False
        )
        
        # Check permissions (creator or removing self)
        if conversation_data.get("creator_id") != current_user.id and participant_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot remove other participants")
        
        # Remove participant (mock implementation)
        participants = conversation_data.get("participants", [])
        if participant_id in participants:
            participants.remove(participant_id)
            
            # Update conversation (mock)
            # In production, update database
            
            return {
                "success": True,
                "data": {
                    "conversation_id": conversation_id,
                    "removed_participant": participant_id,
                    "total_participants": len(participants)
                },
                "message": "Participant removed successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Participant not found in conversation")
        
    except ChatServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove participant: {str(e)}")

@router.get("/analytics/summary", response_model=Dict[str, Any])
async def get_chat_analytics(
    timeframe: str = Query("week", regex="^(day|week|month|all)$"),
    current_user: User = Depends(get_current_user)
):
    """
    Get chat analytics summary for the user
    """
    try:
        # Mock analytics data (replace with actual analytics service)
        analytics = {
            "timeframe": timeframe,
            "user_id": current_user.id,
            "summary": {
                "total_conversations": 12,
                "active_conversations": 8,
                "total_messages_sent": 156,
                "total_messages_received": 203,
                "average_response_time": 45,  # seconds
                "most_active_day": "Tuesday"
            },
            "conversation_types": {
                "template_request": 5,
                "generation_discussion": 3,
                "support": 2,
                "general": 2
            },
            "activity_trends": {
                "daily_messages": [12, 18, 25, 15, 22, 19, 8],
                "peak_hour": 14,
                "conversation_growth": 15.5  # percentage
            }
        }
        
        return {
            "success": True,
            "data": analytics,
            "message": "Analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")