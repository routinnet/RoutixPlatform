"""
Thumbnail generation endpoints
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.midjourney_service import midjourney_service, MidjourneyServiceError
from app.workers.generation_tasks import generate_thumbnail_with_midjourney, upscale_thumbnail
from app.core.dependencies import get_current_user
from app.schemas.user import User

router = APIRouter()

class GenerationRequest(BaseModel):
    prompt: str
    template_id: Optional[str] = None
    user_face_url: Optional[str] = None
    user_logo_url: Optional[str] = None
    custom_text: Optional[str] = None
    aspect_ratio: str = "16:9"
    model: str = "v6"

class UpscaleRequest(BaseModel):
    task_id: str
    service: str
    upscale_index: int = 1

@router.post("/generate", response_model=Dict[str, Any])
async def generate_thumbnail(
    request: GenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate thumbnail using Midjourney (direct)
    """
    try:
        result = await midjourney_service.generate_thumbnail(
            prompt=request.prompt,
            template_analysis=None,  # Would need to fetch if template_id provided
            user_face_url=request.user_face_url,
            user_logo_url=request.user_logo_url,
            custom_text=request.custom_text,
            aspect_ratio=request.aspect_ratio,
            model=request.model
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Thumbnail generated successfully"
        }
        
    except MidjourneyServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/generate-async", response_model=Dict[str, Any])
async def generate_thumbnail_async(
    request: GenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Queue thumbnail generation as background task
    """
    try:
        # Prepare generation request
        generation_data = {
            "id": f"gen_{current_user.id}_{int(datetime.utcnow().timestamp())}",
            "user_id": current_user.id,
            "prompt": request.prompt,
            "template_id": request.template_id,
            "user_face_url": request.user_face_url,
            "user_logo_url": request.user_logo_url,
            "custom_text": request.custom_text,
            "aspect_ratio": request.aspect_ratio,
            "model": request.model
        }
        
        task = generate_thumbnail_with_midjourney.delay(generation_data)
        
        return {
            "success": True,
            "task_id": task.id,
            "generation_id": generation_data["id"],
            "status": "queued",
            "message": "Thumbnail generation queued successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue generation: {str(e)}")

@router.post("/upscale", response_model=Dict[str, Any])
async def upscale_image(
    request: UpscaleRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Upscale a generated thumbnail (direct)
    """
    try:
        result = await midjourney_service.upscale_image(
            task_id=request.task_id,
            upscale_index=request.upscale_index,
            service=request.service
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Image upscaled successfully"
        }
        
    except MidjourneyServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upscale failed: {str(e)}")

@router.post("/upscale-async", response_model=Dict[str, Any])
async def upscale_image_async(
    request: UpscaleRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Queue image upscale as background task
    """
    try:
        task = upscale_thumbnail.delay(
            request.task_id,
            request.service,
            request.upscale_index
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "original_task_id": request.task_id,
            "status": "queued",
            "message": "Image upscale queued successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue upscale: {str(e)}")

@router.get("/task-status/{task_id}", response_model=Dict[str, Any])
async def get_generation_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of generation task
    """
    try:
        from app.workers.celery_app import celery_app
        
        result = celery_app.AsyncResult(task_id)
        
        if result.state == 'PENDING':
            response = {
                "task_id": task_id,
                "status": "pending",
                "message": "Task is waiting to be processed"
            }
        elif result.state == 'PROGRESS':
            response = {
                "task_id": task_id,
                "status": "processing",
                "progress": result.info.get('progress', 0),
                "message": result.info.get('message', 'Processing...'),
                "current_status": result.info.get('status', 'unknown')
            }
        elif result.state == 'SUCCESS':
            response = {
                "task_id": task_id,
                "status": "completed",
                "result": result.result
            }
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "status": "failed",
                "error": str(result.info)
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

@router.get("/service-stats", response_model=Dict[str, Any])
async def get_service_stats(current_user: User = Depends(get_current_user)):
    """
    Get Midjourney service statistics
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        stats = await midjourney_service.get_service_stats()
        return {
            "success": True,
            "stats": stats,
            "message": "Service statistics retrieved"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get service stats: {str(e)}")