"""
Generation Service for Routix Platform
Orchestrates the complete thumbnail generation pipeline
"""
import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid
from app.core.config import settings
from app.services.template_service import template_service, TemplateServiceError
from app.services.midjourney_service import midjourney_service, MidjourneyServiceError
from app.services.ai_service import vision_ai_service, embedding_service, AIServiceError
from app.services.redis_service import redis_service
from app.workers.generation_tasks import generate_thumbnail_with_midjourney

import logging
logger = logging.getLogger(__name__)


class GenerationStatus(str, Enum):
    """Generation status enumeration"""
    PENDING = "pending"
    VALIDATING = "validating"
    MATCHING_TEMPLATES = "matching_templates"
    ANALYZING_STYLE = "analyzing_style"
    GENERATING = "generating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class GenerationServiceError(Exception):
    """Custom exception for generation service errors"""
    pass

class GenerationService:
    """Complete generation pipeline orchestration service"""
    
    def __init__(self):
        # Generation configuration
        self.min_credits_required = 1
        self.template_match_threshold = 0.7
        self.max_template_matches = 5
        self.generation_timeout = 900  # 15 minutes
        
        # Cache configuration
        self.cache_ttl = 86400  # 24 hours
        self.progress_ttl = 3600  # 1 hour for progress tracking
        
        # Credit costs
        self.generation_cost = 1
        self.upscale_cost = 1
        self.premium_generation_cost = 2
        
    async def create_generation(
        self,
        user_id: str,
        prompt: str,
        template_id: Optional[str] = None,
        user_face_url: Optional[str] = None,
        user_logo_url: Optional[str] = None,
        custom_text: Optional[str] = None,
        aspect_ratio: str = "16:9",
        model: str = "v6",
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Create a new generation request and start the pipeline
        
        Args:
            user_id: ID of the requesting user
            prompt: Generation prompt
            template_id: Optional template for style reference
            user_face_url: Optional user face for character reference
            user_logo_url: Optional logo for branding
            custom_text: Custom text to include
            aspect_ratio: Image aspect ratio
            model: Midjourney model version
            priority: Generation priority (normal, high)
            
        Returns:
            Generation request data with tracking ID
        """
        try:
            logger.info(f"Creating generation request for user {user_id}")
            
            # Generate unique generation ID
            generation_id = self._generate_id()
            
            # Validate user credits
            await self._validate_user_credits(user_id, priority)
            
            # Create generation request
            generation_request = {
                "id": generation_id,
                "user_id": user_id,
                "prompt": prompt,
                "template_id": template_id,
                "user_face_url": user_face_url,
                "user_logo_url": user_logo_url,
                "custom_text": custom_text,
                "aspect_ratio": aspect_ratio,
                "model": model,
                "priority": priority,
                "status": GenerationStatus.PENDING,
                "progress": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "estimated_completion": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
                "credits_cost": self._calculate_credits_cost(priority),
                "metadata": {
                    "pipeline_version": "1.0",
                    "ai_services_used": []
                }
            }
            
            # Cache generation request
            await self._cache_generation_data(generation_id, generation_request)
            
            # Start generation pipeline
            pipeline_task_id = await self._start_generation_pipeline(generation_request)
            generation_request["pipeline_task_id"] = pipeline_task_id
            
            # Update cache with task ID
            await self._cache_generation_data(generation_id, generation_request)
            
            # Track generation start
            await self._track_generation_event(generation_id, "created", user_id)
            
            logger.info(f"Generation request created: {generation_id}")
            
            return {
                "generation": generation_request,
                "message": "Generation started successfully"
            }
            
        except Exception as e:
            logger.info(f"Generation creation failed: {e}")
            raise GenerationServiceError(f"Failed to create generation: {str(e)}")
    
    async def get_generation_status(
        self,
        generation_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get generation status and progress
        
        Args:
            generation_id: Generation ID
            user_id: Optional user ID for ownership validation
            
        Returns:
            Generation status and progress data
        """
        try:
            # Get generation data
            generation_data = await self._get_cached_generation_data(generation_id)
            
            if not generation_data:
                raise GenerationServiceError(f"Generation not found: {generation_id}")
            
            # Validate ownership if user_id provided
            if user_id and generation_data.get("user_id") != user_id:
                raise GenerationServiceError("Access denied")
            
            # Get real-time progress from Celery task
            pipeline_task_id = generation_data.get("pipeline_task_id")
            if pipeline_task_id:
                task_progress = await self._get_task_progress(pipeline_task_id)
                if task_progress:
                    generation_data.update(task_progress)
            
            # Calculate time estimates
            generation_data["time_estimates"] = self._calculate_time_estimates(generation_data)
            
            return generation_data
            
        except Exception as e:
            logger.info(f"Failed to get generation status {generation_id}: {e}")
            raise GenerationServiceError(f"Failed to get status: {str(e)}")
    
    async def get_generation_result(
        self,
        generation_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get final generation result
        
        Args:
            generation_id: Generation ID
            user_id: Optional user ID for ownership validation
            
        Returns:
            Final generation result with image URLs
        """
        try:
            # Get generation data
            generation_data = await self._get_cached_generation_data(generation_id)
            
            if not generation_data:
                raise GenerationServiceError(f"Generation not found: {generation_id}")
            
            # Validate ownership
            if user_id and generation_data.get("user_id") != user_id:
                raise GenerationServiceError("Access denied")
            
            # Check if generation is completed
            if generation_data.get("status") != GenerationStatus.COMPLETED:
                raise GenerationServiceError(f"Generation not completed. Status: {generation_data.get('status')}")
            
            # Get result data
            result_data = generation_data.get("result", {})
            
            if not result_data.get("image_url"):
                raise GenerationServiceError("No image result available")
            
            # Track result access
            await self._track_generation_event(generation_id, "result_accessed", user_id)
            
            # Prepare enhanced result
            enhanced_result = {
                "generation_id": generation_id,
                "status": generation_data["status"],
                "image_url": result_data["image_url"],
                "generation_metadata": result_data.get("generation_metadata", {}),
                "template_used": generation_data.get("template_used"),
                "style_analysis": generation_data.get("style_analysis"),
                "credits_used": generation_data.get("credits_cost", 0),
                "generation_time": result_data.get("generation_time", 0),
                "quality_score": result_data.get("generation_metadata", {}).get("quality_score", 0.8),
                "completed_at": generation_data.get("completed_at")
            }
            
            return enhanced_result
            
        except Exception as e:
            logger.info(f"Failed to get generation result {generation_id}: {e}")
            raise GenerationServiceError(f"Failed to get result: {str(e)}")
    
    async def upscale_generation(
        self,
        generation_id: str,
        user_id: str,
        upscale_index: int = 1
    ) -> Dict[str, Any]:
        """
        Upscale a completed generation
        
        Args:
            generation_id: Original generation ID
            user_id: User requesting upscale
            upscale_index: Which image to upscale (1-4)
            
        Returns:
            Upscale request data
        """
        try:
            logger.info(f"Starting upscale for generation {generation_id}")
            
            # Get original generation
            generation_data = await self._get_cached_generation_data(generation_id)
            
            if not generation_data:
                raise GenerationServiceError(f"Generation not found: {generation_id}")
            
            # Validate ownership
            if generation_data.get("user_id") != user_id:
                raise GenerationServiceError("Access denied")
            
            # Validate generation is completed
            if generation_data.get("status") != GenerationStatus.COMPLETED:
                raise GenerationServiceError("Can only upscale completed generations")
            
            # Validate user credits for upscale
            await self._validate_user_credits(user_id, "normal", self.upscale_cost)
            
            # Get original Midjourney task info
            result_data = generation_data.get("result", {})
            original_task_id = result_data.get("task_id") or result_data.get("job_id")
            service_used = result_data.get("generation_metadata", {}).get("midjourney_service", "goapi")
            
            if not original_task_id:
                raise GenerationServiceError("Original generation task ID not found")
            
            # Create upscale request
            upscale_id = self._generate_id()
            upscale_request = {
                "id": upscale_id,
                "original_generation_id": generation_id,
                "user_id": user_id,
                "upscale_index": upscale_index,
                "status": GenerationStatus.PENDING,
                "progress": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "credits_cost": self.upscale_cost,
                "original_task_id": original_task_id,
                "service": service_used
            }
            
            # Start upscale process
            try:
                upscale_result = await midjourney_service.upscale_image(
                    original_task_id, upscale_index, service_used
                )
                
                upscale_request.update({
                    "status": GenerationStatus.COMPLETED,
                    "progress": 100,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "result": upscale_result
                })
                
                # Deduct credits
                await self._deduct_user_credits(user_id, self.upscale_cost)
                
                # Track upscale completion
                await self._track_generation_event(upscale_id, "upscale_completed", user_id)
                
            except MidjourneyServiceError as e:
                upscale_request.update({
                    "status": GenerationStatus.FAILED,
                    "error": str(e),
                    "failed_at": datetime.now(timezone.utc).isoformat()
                })
                raise GenerationServiceError(f"Upscale failed: {str(e)}")
            
            # Cache upscale request
            await self._cache_generation_data(upscale_id, upscale_request)
            
            logger.info(f"Upscale completed: {upscale_id}")
            
            return {
                "upscale": upscale_request,
                "message": "Upscale completed successfully"
            }
            
        except Exception as e:
            logger.info(f"Upscale failed for generation {generation_id}: {e}")
            raise GenerationServiceError(f"Upscale failed: {str(e)}")
    
    async def get_generation_history(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get user's generation history
        
        Args:
            user_id: User ID
            limit: Maximum results to return
            offset: Results offset for pagination
            status_filter: Optional status filter
            
        Returns:
            User's generation history
        """
        try:
            # Get user's generations (mock implementation)
            generations = await self._get_user_generations(user_id, limit, offset, status_filter)
            
            # Calculate summary statistics
            total_generations = len(generations)
            completed_generations = len([g for g in generations if g.get("status") == GenerationStatus.COMPLETED])
            total_credits_used = sum(g.get("credits_cost", 0) for g in generations)
            
            history_data = {
                "generations": generations,
                "pagination": {
                    "total": total_generations,
                    "limit": limit,
                    "offset": offset,
                    "has_more": total_generations == limit  # Simple check
                },
                "summary": {
                    "total_generations": total_generations,
                    "completed_generations": completed_generations,
                    "success_rate": (completed_generations / total_generations * 100) if total_generations > 0 else 0,
                    "total_credits_used": total_credits_used
                }
            }
            
            return history_data
            
        except Exception as e:
            logger.info(f"Failed to get generation history for user {user_id}: {e}")
            raise GenerationServiceError(f"Failed to get history: {str(e)}")
    
    async def cancel_generation(
        self,
        generation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Cancel a pending or running generation
        
        Args:
            generation_id: Generation ID to cancel
            user_id: User requesting cancellation
            
        Returns:
            Cancellation result
        """
        try:
            # Get generation data
            generation_data = await self._get_cached_generation_data(generation_id)
            
            if not generation_data:
                raise GenerationServiceError(f"Generation not found: {generation_id}")
            
            # Validate ownership
            if generation_data.get("user_id") != user_id:
                raise GenerationServiceError("Access denied")
            
            # Check if cancellable
            current_status = generation_data.get("status")
            if current_status in [GenerationStatus.COMPLETED, GenerationStatus.FAILED, GenerationStatus.CANCELLED]:
                raise GenerationServiceError(f"Cannot cancel generation with status: {current_status}")
            
            # Cancel Celery task if running
            pipeline_task_id = generation_data.get("pipeline_task_id")
            if pipeline_task_id:
                try:
                    from app.workers.celery_app import celery_app
                    celery_app.control.revoke(pipeline_task_id, terminate=True)
                except Exception as e:
                    logger.info(f"Failed to cancel Celery task {pipeline_task_id}: {e}")
            
            # Update generation status
            generation_data.update({
                "status": GenerationStatus.CANCELLED,
                "cancelled_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Update cache
            await self._cache_generation_data(generation_id, generation_data)
            
            # Track cancellation
            await self._track_generation_event(generation_id, "cancelled", user_id)
            
            return {
                "generation_id": generation_id,
                "status": GenerationStatus.CANCELLED,
                "message": "Generation cancelled successfully"
            }
            
        except Exception as e:
            logger.info(f"Failed to cancel generation {generation_id}: {e}")
            raise GenerationServiceError(f"Cancellation failed: {str(e)}")
    
    # Private helper methods
    
    def _generate_id(self) -> str:
        """Generate unique ID for generations"""
        return f"gen_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    async def _validate_user_credits(self, user_id: str, priority: str, cost: Optional[int] = None) -> None:
        """Validate user has sufficient credits"""
        required_credits = cost or self._calculate_credits_cost(priority)
        
        # Mock credit validation (replace with actual user service)
        user_credits = await self._get_user_credits(user_id)
        
        if user_credits < required_credits:
            raise GenerationServiceError(f"Insufficient credits. Required: {required_credits}, Available: {user_credits}")
    
    def _calculate_credits_cost(self, priority: str) -> int:
        """Calculate credits cost based on priority"""
        if priority == "high":
            return self.premium_generation_cost
        return self.generation_cost
    
    async def _start_generation_pipeline(self, generation_request: Dict[str, Any]) -> str:
        """Start the generation pipeline as background task"""
        try:
            # Queue generation task
            task = generate_thumbnail_with_midjourney.delay(generation_request)
            
            logger.info(f"Generation pipeline started: {task.id}")
            return task.id
            
        except Exception as e:
            raise GenerationServiceError(f"Failed to start pipeline: {str(e)}")
    
    async def _cache_generation_data(self, generation_id: str, data: Dict[str, Any]) -> None:
        """Cache generation data"""
        cache_key = f"generation:{generation_id}"
        await redis_service.set(cache_key, data, self.cache_ttl)
    
    async def _get_cached_generation_data(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """Get cached generation data"""
        cache_key = f"generation:{generation_id}"
        return await redis_service.get(cache_key)
    
    async def _track_generation_event(self, generation_id: str, event: str, user_id: str) -> None:
        """Track generation analytics event"""
        event_data = {
            "generation_id": generation_id,
            "event": event,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        analytics_key = f"analytics:generation:{generation_id}"
        await redis_service.lpush(analytics_key, event_data)
        await redis_service.expire(analytics_key, 86400 * 30)  # 30 days
    
    async def _get_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get Celery task progress"""
        try:
            from app.workers.celery_app import celery_app
            
            result = celery_app.AsyncResult(task_id)
            
            if result.state == 'PENDING':
                return {"status": GenerationStatus.PENDING, "progress": 0}
            elif result.state == 'PROGRESS':
                return {
                    "status": result.info.get('status', GenerationStatus.GENERATING),
                    "progress": result.info.get('progress', 0),
                    "message": result.info.get('message', 'Processing...')
                }
            elif result.state == 'SUCCESS':
                return {"status": GenerationStatus.COMPLETED, "progress": 100, "result": result.result}
            else:  # FAILURE
                return {"status": GenerationStatus.FAILED, "error": str(result.info)}
                
        except Exception as e:
            logger.info(f"Failed to get task progress for {task_id}: {e}")
            return None
    
    def _calculate_time_estimates(self, generation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate time estimates for generation"""
        created_at = datetime.fromisoformat(generation_data["created_at"])
        now = datetime.now(timezone.utc)
        elapsed = (now - created_at).total_seconds()
        
        # Estimate based on current progress
        progress = generation_data.get("progress", 0)
        if progress > 0:
            estimated_total = elapsed / (progress / 100)
            remaining = max(0, estimated_total - elapsed)
        else:
            remaining = 600  # Default 10 minutes
        
        return {
            "elapsed_seconds": int(elapsed),
            "estimated_remaining_seconds": int(remaining),
            "estimated_completion": (now + timedelta(seconds=remaining)).isoformat()
        }
    
    async def _get_user_credits(self, user_id: str) -> int:
        """Get user's current credits (mock implementation)"""
        # Mock implementation - replace with actual user service
        return 100
    
    async def _deduct_user_credits(self, user_id: str, amount: int) -> None:
        """Deduct credits from user account"""
        # Mock implementation - replace with actual user service
        logger.info(f"Deducting {amount} credits from user {user_id}")
    
    async def _get_user_generations(
        self,
        user_id: str,
        limit: int,
        offset: int,
        status_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get user's generations (mock implementation)"""
        # Mock implementation - replace with actual database query
        mock_generations = []
        
        for i in range(limit):
            generation_id = f"gen_mock_{i + offset}"
            mock_generations.append({
                "id": generation_id,
                "user_id": user_id,
                "prompt": f"Mock generation prompt {i + offset}",
                "status": GenerationStatus.COMPLETED if i % 3 == 0 else GenerationStatus.PENDING,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat(),
                "credits_cost": self.generation_cost,
                "progress": 100 if i % 3 == 0 else 50
            })
        
        # Apply status filter
        if status_filter:
            mock_generations = [g for g in mock_generations if g["status"] == status_filter]
        
        return mock_generations

# Global generation service instance
generation_service = GenerationService()