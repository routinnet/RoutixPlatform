"""
Template management endpoints
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.template_service import template_service, TemplateServiceError
from app.core.dependencies import get_current_user
from app.schemas.user import User

router = APIRouter()

class TemplateUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class BatchProcessRequest(BaseModel):
    template_ids: List[str]
    operation: str
    parameters: Optional[Dict[str, Any]] = None

@router.post("/upload", response_model=Dict[str, Any])
async def upload_template(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string of tags
    auto_analyze: bool = Form(True),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a new template with automatic AI analysis
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse tags if provided
        parsed_tags = []
        if tags:
            try:
                import json
                parsed_tags = json.loads(tags)
            except json.JSONDecodeError:
                parsed_tags = [tag.strip() for tag in tags.split(",")]
        
        # Upload and process template
        result = await template_service.upload_template(
            file_content=file_content,
            filename=file.filename,
            user_id=current_user.id,
            title=title,
            description=description,
            category=category,
            tags=parsed_tags,
            auto_analyze=auto_analyze
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Template uploaded successfully"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/search", response_model=Dict[str, Any])
async def search_templates(
    query: Optional[str] = Query(None, description="Text query for semantic search"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    similarity_threshold: float = Query(0.7, ge=0.0, le=1.0, description="Minimum similarity score"),
    current_user: User = Depends(get_current_user)
):
    """
    Search templates using vector similarity and filters
    """
    try:
        # Parse tags if provided
        parsed_tags = None
        if tags:
            parsed_tags = [tag.strip() for tag in tags.split(",")]
        
        # Perform search
        results = await template_service.search_templates(
            query=query,
            category=category,
            tags=parsed_tags,
            user_id=user_id,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        return {
            "success": True,
            "data": results,
            "message": "Search completed successfully"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/{template_id}", response_model=Dict[str, Any])
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get template details by ID
    """
    try:
        template_data = await template_service.get_template(
            template_id=template_id,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": template_data,
            "message": "Template retrieved successfully"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")

@router.put("/{template_id}", response_model=Dict[str, Any])
async def update_template(
    template_id: str,
    updates: TemplateUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update template metadata
    """
    try:
        # Convert to dict and remove None values
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        updated_template = await template_service.update_template(
            template_id=template_id,
            user_id=current_user.id,
            updates=update_data
        )
        
        return {
            "success": True,
            "data": updated_template,
            "message": "Template updated successfully"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.delete("/{template_id}", response_model=Dict[str, Any])
async def delete_template(
    template_id: str,
    soft_delete: bool = Query(True, description="Whether to soft delete (true) or hard delete (false)"),
    current_user: User = Depends(get_current_user)
):
    """
    Delete template (soft delete by default)
    """
    try:
        result = await template_service.delete_template(
            template_id=template_id,
            user_id=current_user.id,
            soft_delete=soft_delete
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Template deleted successfully"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@router.get("/popular/trending", response_model=Dict[str, Any])
async def get_popular_templates(
    timeframe: str = Query("week", regex="^(day|week|month|all)$", description="Time period for popularity"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Get popular/trending templates based on analytics
    """
    try:
        results = await template_service.get_popular_templates(
            timeframe=timeframe,
            category=category,
            limit=limit
        )
        
        return {
            "success": True,
            "data": results,
            "message": "Popular templates retrieved successfully"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get popular templates: {str(e)}")

@router.post("/batch-process", response_model=Dict[str, Any])
async def batch_process_templates(
    request: BatchProcessRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Process multiple templates in batch (admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = await template_service.batch_process_templates(
            template_ids=request.template_ids,
            operation=request.operation,
            parameters=request.parameters
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Batch processing completed"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@router.get("/analytics/{template_id}", response_model=Dict[str, Any])
async def get_template_analytics(
    template_id: str,
    timeframe: str = Query("week", regex="^(day|week|month|all)$"),
    current_user: User = Depends(get_current_user)
):
    """
    Get template analytics data
    """
    try:
        # Check if user owns template or is admin
        template_data = await template_service.get_template(template_id)
        
        if template_data.get("user_id") != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Mock analytics data (replace with actual implementation)
        analytics = {
            "template_id": template_id,
            "timeframe": timeframe,
            "metrics": {
                "views": 150,
                "downloads": 25,
                "likes": 12,
                "shares": 3
            },
            "trends": {
                "daily_views": [10, 15, 20, 18, 25, 30, 22],
                "peak_day": "Friday",
                "growth_rate": 15.5
            },
            "demographics": {
                "top_categories": ["gaming", "tech", "design"],
                "user_types": {"creator": 60, "business": 30, "personal": 10}
            }
        }
        
        return {
            "success": True,
            "data": analytics,
            "message": "Analytics retrieved successfully"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/{template_id}/like", response_model=Dict[str, Any])
async def like_template(
    template_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Like/unlike a template
    """
    try:
        # Get template data
        template_data = await template_service.get_template(template_id)
        
        # Mock like functionality (implement proper like tracking)
        current_likes = template_data.get("like_count", 0)
        new_like_count = current_likes + 1
        
        # Update template
        await template_service.update_template(
            template_id=template_id,
            user_id=template_data["user_id"],  # Use template owner for update
            updates={"like_count": new_like_count}
        )
        
        return {
            "success": True,
            "data": {
                "template_id": template_id,
                "like_count": new_like_count,
                "action": "liked"
            },
            "message": "Template liked successfully"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to like template: {str(e)}")

@router.get("/user/{user_id}/templates", response_model=Dict[str, Any])
async def get_user_templates(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """
    Get templates by user ID
    """
    try:
        # Use search with user filter
        results = await template_service.search_templates(
            user_id=user_id,
            limit=limit
        )
        
        # Apply offset (simple implementation)
        templates = results["results"][offset:offset + limit]
        
        return {
            "success": True,
            "data": {
                "templates": templates,
                "total": len(results["results"]),
                "limit": limit,
                "offset": offset
            },
            "message": "User templates retrieved successfully"
        }
        
    except TemplateServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user templates: {str(e)}")