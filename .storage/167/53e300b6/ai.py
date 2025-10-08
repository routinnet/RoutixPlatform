"""
AI service endpoints
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from app.services.ai_service import vision_ai_service, AIServiceError
from app.services.embedding_service import embedding_service
from app.workers.ai_tasks import analyze_template_task, generate_embedding_task
from app.core.dependencies import get_current_user
from app.schemas.user import User

router = APIRouter()

@router.post("/analyze-image", response_model=Dict[str, Any])
async def analyze_image(
    image_url: str,
    template_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze image using AI vision services
    """
    try:
        result = await vision_ai_service.analyze_template_image(image_url, template_id)
        return {
            "success": True,
            "data": result,
            "message": "Image analysis completed successfully"
        }
    except AIServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-image-async", response_model=Dict[str, Any])
async def analyze_image_async(
    image_url: str,
    template_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Queue image analysis as background task
    """
    try:
        task = analyze_template_task.delay(template_id or f"temp_{current_user.id}", image_url)
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "queued",
            "message": "Image analysis queued successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue analysis: {str(e)}")

@router.post("/generate-embedding", response_model=Dict[str, Any])
async def generate_embedding(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Generate embedding for text
    """
    try:
        embedding = await embedding_service.generate_embedding(text)
        return {
            "success": True,
            "embedding": embedding,
            "dimensions": len(embedding),
            "message": "Embedding generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

@router.post("/generate-embedding-async", response_model=Dict[str, Any])
async def generate_embedding_async(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Queue embedding generation as background task
    """
    try:
        task = generate_embedding_task.delay(text)
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "queued",
            "message": "Embedding generation queued successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue embedding generation: {str(e)}")

@router.get("/task-status/{task_id}", response_model=Dict[str, Any])
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of AI task
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
                "message": result.info.get('message', 'Processing...')
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

@router.post("/test-ai-services", response_model=Dict[str, Any])
async def test_ai_services(current_user: User = Depends(get_current_user)):
    """
    Test AI services availability (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Test Gemini availability
        gemini_available = vision_ai_service.gemini_model is not None
        
        # Test OpenAI availability
        openai_available = vision_ai_service.openai_client is not None
        
        # Test embedding service
        embedding_available = embedding_service.openai_client is not None
        
        return {
            "success": True,
            "services": {
                "gemini_vision": {
                    "available": gemini_available,
                    "status": "configured" if gemini_available else "missing_api_key"
                },
                "openai_vision": {
                    "available": openai_available,
                    "status": "configured" if openai_available else "missing_api_key"
                },
                "openai_embeddings": {
                    "available": embedding_available,
                    "status": "configured" if embedding_available else "missing_api_key"
                }
            },
            "message": "AI services status checked"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service check failed: {str(e)}")