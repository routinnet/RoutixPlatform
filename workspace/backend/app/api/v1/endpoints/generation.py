"""
Generation orchestration endpoints
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from app.services.generation_service import generation_service, GenerationServiceError, GenerationStatus
from app.core.dependencies import get_current_user
from app.schemas.user import User

router = APIRouter()

class GenerationCreateRequest(BaseModel):
    prompt: str
    template_id: Optional[str] = None
    user_face_url: Optional[str] = None
    user_logo_url: Optional[str] = None
    custom_text: Optional[str] = None
    aspect_ratio: str = "16:9"
    model: str = "v6"
    priority: str = "normal"

class UpscaleRequest(BaseModel):
    upscale_index: int = 1

@router.post("/create", response_model=Dict[str, Any])
async def create_generation(
    request: GenerationCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new generation request and start the pipeline
    """
    try:
        result = await generation_service.create_generation(
            user_id=current_user.id,
            prompt=request.prompt,
            template_id=request.template_id,
            user_face_url=request.user_face_url,
            user_logo_url=request.user_logo_url,
            custom_text=request.custom_text,
            aspect_ratio=request.aspect_ratio,
            model=request.model,
            priority=request.priority
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Generation started successfully"
        }
        
    except GenerationServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.get("/{generation_id}/status", response_model=Dict[str, Any])
async def get_generation_status(
    generation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get generation status and progress
    """
    try:
        status_data = await generation_service.get_generation_status(
            generation_id=generation_id,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": status_data,
            "message": "Status retrieved successfully"
        }
        
    except GenerationServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/{generation_id}/result", response_model=Dict[str, Any])
async def get_generation_result(
    generation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get final generation result
    """
    try:
        result_data = await generation_service.get_generation_result(
            generation_id=generation_id,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": result_data,
            "message": "Result retrieved successfully"
        }
        
    except GenerationServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get result: {str(e)}")

@router.post("/{generation_id}/upscale", response_model=Dict[str, Any])
async def upscale_generation(
    generation_id: str,
    request: UpscaleRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Upscale a completed generation
    """
    try:
        result = await generation_service.upscale_generation(
            generation_id=generation_id,
            user_id=current_user.id,
            upscale_index=request.upscale_index
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Upscale completed successfully"
        }
        
    except GenerationServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upscale failed: {str(e)}")

@router.get("/history", response_model=Dict[str, Any])
async def get_generation_history(
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Results offset for pagination"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's generation history
    """
    try:
        history_data = await generation_service.get_generation_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            status_filter=status
        )
        
        return {
            "success": True,
            "data": history_data,
            "message": "History retrieved successfully"
        }
        
    except GenerationServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.delete("/{generation_id}/cancel", response_model=Dict[str, Any])
async def cancel_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a pending or running generation
    """
    try:
        result = await generation_service.cancel_generation(
            generation_id=generation_id,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Generation cancelled successfully"
        }
        
    except GenerationServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cancellation failed: {str(e)}")

@router.get("/queue/status", response_model=Dict[str, Any])
async def get_queue_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get generation queue status and statistics
    """
    try:
        # Mock queue status (replace with actual Celery queue inspection)
        queue_stats = {
            "active_generations": 5,
            "queued_generations": 12,
            "average_wait_time": 180,  # seconds
            "estimated_processing_time": 300,  # seconds
            "queue_health": "healthy",
            "worker_status": {
                "active_workers": 3,
                "total_workers": 4,
                "busy_workers": 2
            },
            "recent_completions": 45,
            "success_rate": 94.5
        }
        
        return {
            "success": True,
            "data": queue_stats,
            "message": "Queue status retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get queue status: {str(e)}")

@router.get("/analytics/summary", response_model=Dict[str, Any])
async def get_generation_analytics(
    timeframe: str = Query("week", pattern="^(day|week|month|all)$"),
    current_user: User = Depends(get_current_user)
):
    """
    Get generation analytics summary for the user
    """
    try:
        # Mock analytics data (replace with actual analytics service)
        analytics = {
            "timeframe": timeframe,
            "user_id": current_user.id,
            "summary": {
                "total_generations": 25,
                "completed_generations": 23,
                "failed_generations": 2,
                "success_rate": 92.0,
                "total_credits_used": 27,
                "average_generation_time": 245  # seconds
            },
            "trends": {
                "daily_generations": [3, 5, 2, 4, 6, 3, 2],
                "peak_usage_hour": 14,
                "most_used_aspect_ratio": "16:9",
                "most_used_model": "v6"
            },
            "popular_templates": [
                {"template_id": "tpl_001", "usage_count": 5, "title": "Gaming Thumbnail"},
                {"template_id": "tpl_002", "usage_count": 3, "title": "Tech Review"}
            ]
        }
        
        return {
            "success": True,
            "data": analytics,
            "message": "Analytics retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/user", response_model=Dict[str, Any])
async def get_user_generations(
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Results offset for pagination"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's generation history (alias for /history endpoint)
    """
    try:
        history_data = await generation_service.get_generation_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            status_filter=status
        )
        
        return {
            "success": True,
            "data": history_data,
            "message": "History retrieved successfully"
        }
        
    except GenerationServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.get("/{generation_id}/download", response_model=Dict[str, Any])
async def download_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a completed generation
    """
    try:
        result_data = await generation_service.get_generation_result(
            generation_id=generation_id,
            user_id=current_user.id
        )
        
        # Return download URL
        download_url = result_data.get("thumbnail_url")
        
        return {
            "success": True,
            "data": {
                "generation_id": generation_id,
                "download_url": download_url,
                "filename": f"routix_thumbnail_{generation_id}.png"
            },
            "message": "Download link generated successfully"
        }
        
    except GenerationServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download link: {str(e)}")

@router.post("/{generation_id}/favorite", response_model=Dict[str, Any])
async def favorite_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Mark a generation as favorite
    """
    try:
        from app.services.redis_service import redis_service
        
        # Store favorite in Redis
        favorite_key = f"user:{current_user.id}:favorites"
        await redis_service.sadd(favorite_key, generation_id)
        
        return {
            "success": True,
            "data": {
                "generation_id": generation_id,
                "is_favorite": True
            },
            "message": "Generation marked as favorite"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to favorite generation: {str(e)}")

@router.delete("/{generation_id}/favorite", response_model=Dict[str, Any])
async def unfavorite_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove a generation from favorites
    """
    try:
        from app.services.redis_service import redis_service
        
        # Remove favorite from Redis
        favorite_key = f"user:{current_user.id}:favorites"
        await redis_service.srem(favorite_key, generation_id)
        
        return {
            "success": True,
            "data": {
                "generation_id": generation_id,
                "is_favorite": False
            },
            "message": "Generation removed from favorites"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unfavorite generation: {str(e)}")

@router.post("/{generation_id}/share", response_model=Dict[str, Any])
async def share_generation(
    generation_id: str,
    data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Share a generation (create public share link)
    """
    try:
        import secrets
        from app.services.redis_service import redis_service
        
        # Generate share token
        share_token = secrets.token_urlsafe(16)
        share_key = f"share:{share_token}"
        
        # Store share data in Redis (expires in 30 days)
        share_data = {
            "generation_id": generation_id,
            "user_id": current_user.id,
            "created_at": data.get("created_at", ""),
            "expires_at": data.get("expires_at", "")
        }
        
        await redis_service.set(share_key, str(share_data), 30 * 24 * 60 * 60)
        
        # Create public share URL
        share_url = f"/share/{share_token}"
        
        return {
            "success": True,
            "data": {
                "generation_id": generation_id,
                "share_token": share_token,
                "share_url": share_url,
                "expires_in_days": 30
            },
            "message": "Share link created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create share link: {str(e)}")

@router.delete("/{generation_id}", response_model=Dict[str, Any])
async def delete_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a generation
    """
    try:
        from app.services.redis_service import redis_service
        
        # Verify ownership
        result_data = await generation_service.get_generation_result(
            generation_id=generation_id,
            user_id=current_user.id
        )
        
        # Delete from storage (mock implementation)
        generation_key = f"generation:{generation_id}"
        await redis_service.delete(generation_key)
        
        # Remove from user's history
        user_generations_key = f"user:{current_user.id}:generations"
        await redis_service.lrem(user_generations_key, generation_id, 0)
        
        return {
            "success": True,
            "data": {
                "generation_id": generation_id,
                "deleted": True
            },
            "message": "Generation deleted successfully"
        }
        
    except GenerationServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete generation: {str(e)}")

@router.post("/batch", response_model=Dict[str, Any])
async def create_batch_generation(
    requests: list[GenerationCreateRequest],
    current_user: User = Depends(get_current_user)
):
    """
    Create multiple generation requests in batch
    """
    if not current_user.is_admin and len(requests) > 5:
        raise HTTPException(status_code=403, detail="Non-admin users limited to 5 batch generations")
    
    try:
        batch_results = []
        
        for i, request in enumerate(requests):
            try:
                result = await generation_service.create_generation(
                    user_id=current_user.id,
                    prompt=request.prompt,
                    template_id=request.template_id,
                    user_face_url=request.user_face_url,
                    user_logo_url=request.user_logo_url,
                    custom_text=request.custom_text,
                    aspect_ratio=request.aspect_ratio,
                    model=request.model,
                    priority=request.priority
                )
                
                batch_results.append({
                    "index": i,
                    "status": "queued",
                    "generation_id": result["generation"]["id"],
                    "result": result
                })
                
            except Exception as e:
                batch_results.append({
                    "index": i,
                    "status": "failed",
                    "error": str(e)
                })
        
        batch_summary = {
            "total_requests": len(requests),
            "successful": len([r for r in batch_results if r["status"] == "queued"]),
            "failed": len([r for r in batch_results if r["status"] == "failed"]),
            "results": batch_results
        }
        
        return {
            "success": True,
            "data": batch_summary,
            "message": "Batch generation created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")