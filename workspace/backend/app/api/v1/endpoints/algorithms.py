"""
Algorithm Management Endpoints
Routix Versions CRUD and configuration
"""

from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.dependencies import get_db, get_current_admin_user, get_current_user
from app.models.user import User

router = APIRouter()


class AlgorithmCreateRequest(BaseModel):
    name: str
    version: str
    description: str
    model_type: str
    base_model: str
    is_active: bool = True
    is_premium: bool = False
    credit_cost: int = 1
    max_resolution: str = "1280x720"
    supported_features: List[str] = []
    parameters: Dict[str, Any] = {}


class AlgorithmUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    credit_cost: Optional[int] = None
    max_resolution: Optional[str] = None
    supported_features: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None


@router.get("/")
async def get_algorithms(
    include_inactive: bool = Query(False, description="Include inactive algorithms"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get available Routix Versions (algorithms)
    """
    try:
        # Define available Routix Versions
        algorithms = [
            {
                "id": "routix_v4",
                "name": "Routix V4",
                "version": "4.0",
                "description": "Fast generation with good quality, ideal for quick iterations",
                "model_type": "midjourney",
                "base_model": "midjourney-v4",
                "is_active": True,
                "is_premium": False,
                "credit_cost": 1,
                "max_resolution": "1024x1024",
                "supported_features": ["text_overlay", "template_matching", "basic_customization"],
                "parameters": {
                    "quality": "standard",
                    "speed": "fast",
                    "style": "photorealistic"
                },
                "average_generation_time": 30,
                "success_rate": 95.5,
                "usage_count": 15234
            },
            {
                "id": "routix_v5",
                "name": "Routix V5",
                "version": "5.0",
                "description": "Enhanced quality and detail, better for complex compositions",
                "model_type": "midjourney",
                "base_model": "midjourney-v5",
                "is_active": True,
                "is_premium": False,
                "credit_cost": 1,
                "max_resolution": "1280x720",
                "supported_features": ["text_overlay", "template_matching", "advanced_customization", "face_swap"],
                "parameters": {
                    "quality": "high",
                    "speed": "medium",
                    "style": "photorealistic"
                },
                "average_generation_time": 45,
                "success_rate": 96.8,
                "usage_count": 28456
            },
            {
                "id": "routix_v6",
                "name": "Routix V6",
                "version": "6.0",
                "description": "Latest model with best quality and most accurate results",
                "model_type": "midjourney",
                "base_model": "midjourney-v6",
                "is_active": True,
                "is_premium": False,
                "credit_cost": 2,
                "max_resolution": "1920x1080",
                "supported_features": ["text_overlay", "template_matching", "advanced_customization", "face_swap", "logo_integration"],
                "parameters": {
                    "quality": "ultra",
                    "speed": "medium",
                    "style": "photorealistic"
                },
                "average_generation_time": 60,
                "success_rate": 98.2,
                "usage_count": 42789
            },
            {
                "id": "routix_v7_anime",
                "name": "Routix V7 Anime",
                "version": "7.0-anime",
                "description": "Specialized for anime and manga style thumbnails",
                "model_type": "midjourney",
                "base_model": "niji-6",
                "is_active": True,
                "is_premium": True,
                "credit_cost": 2,
                "max_resolution": "1920x1080",
                "supported_features": ["text_overlay", "template_matching", "anime_style", "character_consistency"],
                "parameters": {
                    "quality": "ultra",
                    "speed": "medium",
                    "style": "anime"
                },
                "average_generation_time": 55,
                "success_rate": 97.5,
                "usage_count": 18923
            },
            {
                "id": "routix_experimental",
                "name": "Routix Experimental",
                "version": "8.0-beta",
                "description": "Cutting-edge features and experimental capabilities",
                "model_type": "mixed",
                "base_model": "custom",
                "is_active": False,
                "is_premium": True,
                "credit_cost": 3,
                "max_resolution": "2560x1440",
                "supported_features": ["all_features", "ai_enhancement", "smart_composition"],
                "parameters": {
                    "quality": "experimental",
                    "speed": "slow",
                    "style": "adaptive"
                },
                "average_generation_time": 90,
                "success_rate": 92.0,
                "usage_count": 1234
            }
        ]
        
        # Filter inactive algorithms if not requested
        if not include_inactive:
            algorithms = [algo for algo in algorithms if algo["is_active"]]
        
        return {
            "success": True,
            "data": {
                "algorithms": algorithms,
                "total": len(algorithms),
                "default_algorithm": "routix_v6"
            },
            "message": "Algorithms retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get algorithms: {str(e)}")


@router.get("/{algorithm_id}")
async def get_algorithm(
    algorithm_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get specific algorithm details
    """
    try:
        # Get all algorithms and find the specific one
        all_algos_response = await get_algorithms(include_inactive=True, db=db)
        algorithms = all_algos_response["data"]["algorithms"]
        
        algorithm = next((algo for algo in algorithms if algo["id"] == algorithm_id), None)
        
        if not algorithm:
            raise HTTPException(status_code=404, detail=f"Algorithm '{algorithm_id}' not found")
        
        return {
            "success": True,
            "data": algorithm,
            "message": "Algorithm retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get algorithm: {str(e)}")


@router.post("/")
async def create_algorithm(
    request: AlgorithmCreateRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create new algorithm (admin only)
    """
    try:
        from app.services.redis_service import redis_service
        import uuid
        
        # Generate algorithm ID
        algorithm_id = f"routix_{request.version.lower().replace('.', '_')}"
        
        # Create algorithm data
        algorithm_data = {
            "id": algorithm_id,
            **request.model_dump(),
            "created_by": current_admin.id,
            "created_at": "",
            "usage_count": 0,
            "average_generation_time": 0,
            "success_rate": 0.0
        }
        
        # Store in Redis (mock implementation)
        algo_key = f"algorithm:{algorithm_id}"
        await redis_service.set(algo_key, str(algorithm_data))
        
        return {
            "success": True,
            "data": algorithm_data,
            "message": "Algorithm created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create algorithm: {str(e)}")


@router.put("/{algorithm_id}")
async def update_algorithm(
    algorithm_id: str,
    request: AlgorithmUpdateRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update algorithm (admin only)
    """
    try:
        # Get current algorithm
        algo_response = await get_algorithm(algorithm_id, db)
        current_algo = algo_response["data"]
        
        # Update with new values
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        current_algo.update(updates)
        current_algo["updated_at"] = ""
        current_algo["updated_by"] = current_admin.id
        
        # Store updated algorithm (mock implementation)
        from app.services.redis_service import redis_service
        algo_key = f"algorithm:{algorithm_id}"
        await redis_service.set(algo_key, str(current_algo))
        
        return {
            "success": True,
            "data": current_algo,
            "message": "Algorithm updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update algorithm: {str(e)}")


@router.delete("/{algorithm_id}")
async def delete_algorithm(
    algorithm_id: str,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete algorithm (admin only) - soft delete by marking as inactive
    """
    try:
        # Get current algorithm
        algo_response = await get_algorithm(algorithm_id, db)
        current_algo = algo_response["data"]
        
        # Mark as inactive instead of deleting
        current_algo["is_active"] = False
        current_algo["deleted_at"] = ""
        current_algo["deleted_by"] = current_admin.id
        
        # Store updated algorithm (mock implementation)
        from app.services.redis_service import redis_service
        algo_key = f"algorithm:{algorithm_id}"
        await redis_service.set(algo_key, str(current_algo))
        
        return {
            "success": True,
            "data": {
                "algorithm_id": algorithm_id,
                "deleted": True
            },
            "message": "Algorithm deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete algorithm: {str(e)}")


@router.get("/stats/performance")
async def get_algorithm_performance_stats(
    timeframe: str = Query("week", pattern="^(day|week|month|all)$"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get performance statistics for all algorithms (admin only)
    """
    try:
        # Mock performance stats
        stats = {
            "timeframe": timeframe,
            "algorithms": [
                {
                    "algorithm_id": "routix_v4",
                    "total_generations": 3421,
                    "success_rate": 95.5,
                    "average_time": 30,
                    "error_rate": 4.5,
                    "user_satisfaction": 4.2
                },
                {
                    "algorithm_id": "routix_v5",
                    "total_generations": 5234,
                    "success_rate": 96.8,
                    "average_time": 45,
                    "error_rate": 3.2,
                    "user_satisfaction": 4.5
                },
                {
                    "algorithm_id": "routix_v6",
                    "total_generations": 8912,
                    "success_rate": 98.2,
                    "average_time": 60,
                    "error_rate": 1.8,
                    "user_satisfaction": 4.8
                },
                {
                    "algorithm_id": "routix_v7_anime",
                    "total_generations": 2145,
                    "success_rate": 97.5,
                    "average_time": 55,
                    "error_rate": 2.5,
                    "user_satisfaction": 4.7
                }
            ],
            "summary": {
                "total_generations": 19712,
                "overall_success_rate": 97.0,
                "most_popular": "routix_v6",
                "fastest": "routix_v4",
                "highest_quality": "routix_v6"
            }
        }
        
        return {
            "success": True,
            "data": stats,
            "message": "Performance stats retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance stats: {str(e)}")