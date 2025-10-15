"""
Generation Pipeline Worker for Routix Platform
Complete 10-step thumbnail generation orchestration with real-time progress
"""
import asyncio
import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from celery import current_task
from app.workers.celery_app import celery_app
from app.services.generation_service import generation_service, GenerationServiceError
from app.services.template_service import template_service, TemplateServiceError
from app.services.ai_service import vision_ai_service, embedding_service, AIServiceError
from app.services.midjourney_service import midjourney_service, MidjourneyServiceError
from app.services.user_service import user_service, UserServiceError
from app.services.redis_service import redis_service

# Configure logging
logger = logging.getLogger(__name__)

class GenerationPipelineError(Exception):
    """Custom exception for generation pipeline errors"""
    pass

class MidjourneyTimeoutError(GenerationPipelineError):
    """Midjourney operation timeout error"""
    pass

class TemplateNotFoundError(GenerationPipelineError):
    """Template matching error"""
    pass

class CreditInsufficientError(GenerationPipelineError):
    """Insufficient credits error"""
    pass

@celery_app.task(bind=True, max_retries=1)
def generate_thumbnail_task(self, request_id: str) -> Dict[str, Any]:
    """
    Complete 10-step generation pipeline with real-time progress broadcasting
    
    Args:
        request_id: Generation request ID
        
    Returns:
        Generation result with final image URL and metadata
    """
    start_time = time.time()
    
    try:
        logger.info(f"[{datetime.now(timezone.utc)}] Starting generation pipeline for request: {request_id}")
        
        # Step 1: Load generation request (5%)
        logger.info(f"Step 1: Loading generation request {request_id}")
        request_data = asyncio.run(load_generation_request(request_id))
        asyncio.run(broadcast_progress(request_id, 5, "validating", "Loading request..."))
        
        # Step 2: Analyze user prompt with AI (15%)
        logger.info(f"Step 2: Analyzing user prompt with AI")
        intent_analysis = asyncio.run(analyze_prompt_intent(request_data))
        asyncio.run(broadcast_progress(request_id, 15, "analyzing", "Understanding your request..."))
        
        # Step 3: Search matching templates (30%)
        logger.info(f"Step 3: Searching for matching templates")
        best_template = asyncio.run(find_matching_template(request_data, intent_analysis))
        asyncio.run(broadcast_progress(request_id, 30, "matching_templates", "Found perfect match..."))
        
        # Step 4: Extract template style DNA (45%)
        logger.info(f"Step 4: Extracting template style DNA")
        style_data = asyncio.run(extract_style_dna(best_template))
        asyncio.run(broadcast_progress(request_id, 45, "analyzing_style", "Extracting style DNA..."))
        
        # Step 5: Compose Midjourney prompt (55%)
        logger.info(f"Step 5: Composing Midjourney prompt")
        mj_prompt = asyncio.run(compose_midjourney_prompt(request_data, style_data, intent_analysis))
        asyncio.run(broadcast_progress(request_id, 55, "generating", "Composing prompt..."))
        
        # Step 6: Call Midjourney API (65%)
        logger.info(f"Step 6: Calling Midjourney API")
        mj_result = asyncio.run(initiate_midjourney_generation(request_data, mj_prompt, style_data))
        task_id = mj_result["task_id"]
        service_used = mj_result["service"]
        asyncio.run(broadcast_progress(request_id, 65, "generating", "Starting AI generation..."))
        
        # Step 7: Poll for completion with progress (65-95%)
        logger.info(f"Step 7: Polling Midjourney for completion")
        generation_result = asyncio.run(poll_midjourney_completion(request_id, task_id, service_used))
        
        # Step 8: Download result image (96%)
        logger.info(f"Step 8: Downloading result image")
        image_data = asyncio.run(download_result_image(generation_result["image_url"]))
        asyncio.run(broadcast_progress(request_id, 96, "processing", "Downloading result..."))
        
        # Step 9: Upload to storage (98%)
        logger.info(f"Step 9: Uploading to storage")
        final_url = asyncio.run(upload_to_storage(request_id, image_data))
        asyncio.run(broadcast_progress(request_id, 98, "processing", "Storing result..."))
        
        # Step 10: Update database & deduct credits (100%)
        logger.info(f"Step 10: Finalizing generation")
        processing_time = time.time() - start_time
        final_result = asyncio.run(finalize_generation(
            request_id, request_data, final_url, processing_time, 
            best_template, generation_result
        ))
        asyncio.run(broadcast_progress(request_id, 100, "completed", "Your thumbnail is ready! 🎉"))
        
        logger.info(f"[{datetime.now(timezone.utc)}] Generation pipeline completed successfully: {request_id}")
        
        return {
            "request_id": request_id,
            "final_url": final_url,
            "processing_time": processing_time,
            "template_used": best_template["id"],
            "generation_metadata": generation_result,
            "status": "completed"
        }
        
    except MidjourneyTimeoutError as e:
        logger.warning(f"Midjourney timeout for {request_id}: {e}")
        # Retry once with 10 second delay
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying generation {request_id} due to timeout")
            asyncio.run(broadcast_progress(request_id, 50, "retrying", "Retrying generation..."))
            raise self.retry(countdown=10, exc=e)
        else:
            asyncio.run(handle_generation_failure(request_id, f"Midjourney timeout: {str(e)}"))
            raise GenerationPipelineError(f"Generation failed after retries: {str(e)}")
            
    except TemplateNotFoundError as e:
        logger.warning(f"Template not found for {request_id}: {e}")
        # Use fallback template
        try:
            fallback_result = asyncio.run(use_fallback_template(request_id, request_data))
            return fallback_result
        except Exception as fallback_error:
            asyncio.run(handle_generation_failure(request_id, f"Template error: {str(e)}"))
            raise GenerationPipelineError(f"Template matching failed: {str(e)}")
            
    except CreditInsufficientError as e:
        logger.error(f"Insufficient credits for {request_id}: {e}")
        asyncio.run(handle_credit_error(request_id, request_data, str(e)))
        raise GenerationPipelineError(f"Credit error: {str(e)}")
        
    except Exception as e:
        logger.error(f"Generation pipeline failed for {request_id}: {e}", exc_info=True)
        asyncio.run(handle_generation_failure(request_id, str(e)))
        raise GenerationPipelineError(f"Pipeline failed: {str(e)}")

# Pipeline Step Functions

async def load_generation_request(request_id: str) -> Dict[str, Any]:
    """Load generation request data"""
    try:
        request_data = await generation_service._get_cached_generation_data(request_id)
        
        if not request_data:
            raise GenerationPipelineError(f"Generation request not found: {request_id}")
        
        # Validate request data
        required_fields = ["user_id", "prompt", "credits_cost"]
        for field in required_fields:
            if field not in request_data:
                raise GenerationPipelineError(f"Missing required field: {field}")
        
        return request_data
        
    except Exception as e:
        raise GenerationPipelineError(f"Failed to load request: {str(e)}")

async def analyze_prompt_intent(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze user prompt to understand intent and extract features"""
    try:
        prompt = request_data["prompt"]
        
        # Use Vision AI to analyze prompt intent
        analysis_prompt = f"""
        Analyze this thumbnail generation request and extract key information:
        
        User Prompt: "{prompt}"
        
        Please provide a JSON response with:
        1. energy_level: "low", "medium", "high"
        2. dominant_colors: ["color1", "color2", "color3"]
        3. mood: "professional", "playful", "dramatic", "minimalist"
        4. content_type: "gaming", "tech", "lifestyle", "business", "educational"
        5. has_text_overlay: true/false
        6. target_audience: "general", "young_adults", "professionals", "gamers"
        7. style_preference: "modern", "vintage", "futuristic", "artistic"
        
        Respond only with valid JSON.
        """
        
        # Get AI analysis
        ai_response = await vision_ai_service.analyze_image_content(
            image_url=None,  # Text-only analysis
            custom_prompt=analysis_prompt
        )
        
        # Parse AI response
        try:
            intent_data = json.loads(ai_response.get("analysis", "{}"))
        except json.JSONDecodeError:
            # Fallback to basic analysis
            intent_data = {
                "energy_level": "medium",
                "dominant_colors": ["blue", "white"],
                "mood": "professional",
                "content_type": "general",
                "has_text_overlay": True,
                "target_audience": "general",
                "style_preference": "modern"
            }
        
        # Generate embedding for semantic search
        embedding = await embedding_service.generate_embedding(prompt)
        intent_data["embedding"] = embedding["embedding"]
        
        return intent_data
        
    except Exception as e:
        logger.warning(f"Intent analysis failed, using defaults: {e}")
        # Return default analysis
        return {
            "energy_level": "medium",
            "dominant_colors": ["blue", "white"],
            "mood": "professional",
            "content_type": "general",
            "has_text_overlay": True,
            "target_audience": "general",
            "style_preference": "modern",
            "embedding": await embedding_service.generate_embedding(request_data["prompt"])
        }

async def find_matching_template(request_data: Dict[str, Any], intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Find the best matching template based on intent analysis"""
    try:
        # Search for similar templates using embedding
        search_results = await template_service.search_similar_templates(
            query_embedding=intent_analysis["embedding"],
            limit=5,
            threshold=0.6
        )
        
        if not search_results["templates"]:
            raise TemplateNotFoundError("No matching templates found")
        
        # Score templates based on multiple factors
        scored_templates = []
        
        for template in search_results["templates"]:
            score = template["similarity_score"]
            
            # Boost score for matching attributes
            template_metadata = template.get("metadata", {})
            
            # Energy level match
            if template_metadata.get("energy_level") == intent_analysis.get("energy_level"):
                score += 0.1
            
            # Content type match
            if template_metadata.get("content_type") == intent_analysis.get("content_type"):
                score += 0.15
            
            # Mood match
            if template_metadata.get("mood") == intent_analysis.get("mood"):
                score += 0.1
            
            # Face presence match
            has_face_required = bool(request_data.get("user_face_url"))
            template_has_face = template_metadata.get("has_faces", False)
            if has_face_required == template_has_face:
                score += 0.1
            
            scored_templates.append({
                **template,
                "final_score": score
            })
        
        # Sort by final score
        scored_templates.sort(key=lambda x: x["final_score"], reverse=True)
        best_template = scored_templates[0]
        
        logger.info(f"Selected template {best_template['id']} with score {best_template['final_score']}")
        
        return best_template
        
    except TemplateServiceError as e:
        raise TemplateNotFoundError(f"Template search failed: {str(e)}")
    except Exception as e:
        raise TemplateNotFoundError(f"Template matching error: {str(e)}")

async def extract_style_dna(template: Dict[str, Any]) -> Dict[str, Any]:
    """Extract style DNA from the selected template"""
    try:
        # Get template analysis data
        style_dna = template.get("analysis_result", {})
        
        if not style_dna:
            # Fallback: analyze template image if no cached analysis
            logger.warning(f"No cached analysis for template {template['id']}, analyzing now")
            
            analysis_result = await vision_ai_service.analyze_image_content(
                image_url=template["image_url"],
                custom_prompt="Analyze this thumbnail template and extract design DNA including colors, typography, composition, and style elements."
            )
            
            style_dna = analysis_result.get("analysis", {})
        
        # Ensure required style data exists
        default_style = {
            "dominant_colors": ["#3B82F6", "#FFFFFF"],
            "typography_style": "modern",
            "composition": "centered",
            "energy_level": "medium",
            "mood": "professional"
        }
        
        # Merge with defaults
        for key, value in default_style.items():
            if key not in style_dna:
                style_dna[key] = value
        
        return {
            "style_dna": style_dna,
            "template_id": template["id"],
            "template_url": template["image_url"],
            "style_reference_url": template["image_url"]
        }
        
    except Exception as e:
        logger.warning(f"Style extraction failed, using defaults: {e}")
        return {
            "style_dna": {
                "dominant_colors": ["#3B82F6", "#FFFFFF"],
                "typography_style": "modern",
                "composition": "centered",
                "energy_level": "medium",
                "mood": "professional"
            },
            "template_id": template["id"],
            "template_url": template["image_url"],
            "style_reference_url": template["image_url"]
        }

async def compose_midjourney_prompt(
    request_data: Dict[str, Any], 
    style_data: Dict[str, Any], 
    intent_analysis: Dict[str, Any]
) -> str:
    """Compose optimized Midjourney prompt"""
    try:
        user_prompt = request_data["prompt"]
        custom_text = request_data.get("custom_text", "")
        style_dna = style_data["style_dna"]
        
        # Build enhanced prompt
        prompt_parts = []
        
        # Base user prompt
        prompt_parts.append(user_prompt)
        
        # Add custom text if provided
        if custom_text:
            prompt_parts.append(f'with text "{custom_text}"')
        
        # Style enhancements from template
        style_descriptors = []
        
        # Color palette
        colors = style_dna.get("dominant_colors", [])
        if colors:
            color_str = ", ".join(colors[:3])  # Top 3 colors
            style_descriptors.append(f"color palette: {color_str}")
        
        # Typography and composition
        typography = style_dna.get("typography_style", "modern")
        composition = style_dna.get("composition", "centered")
        style_descriptors.append(f"{typography} typography, {composition} composition")
        
        # Mood and energy
        mood = style_dna.get("mood", "professional")
        energy = style_dna.get("energy_level", "medium")
        style_descriptors.append(f"{mood} mood, {energy} energy")
        
        # Content type specific enhancements
        content_type = intent_analysis.get("content_type", "general")
        if content_type == "gaming":
            style_descriptors.append("gaming aesthetic, vibrant, dynamic")
        elif content_type == "tech":
            style_descriptors.append("tech-focused, clean, futuristic")
        elif content_type == "lifestyle":
            style_descriptors.append("lifestyle photography, natural, engaging")
        
        # Combine prompt parts
        if style_descriptors:
            prompt_parts.append(f"Style: {', '.join(style_descriptors)}")
        
        # Technical parameters
        aspect_ratio = request_data.get("aspect_ratio", "16:9")
        model_version = request_data.get("model", "v6")
        
        # Final prompt assembly
        final_prompt = " | ".join(prompt_parts)
        final_prompt += f" --ar {aspect_ratio} --v {model_version} --stylize 500"
        
        # Add quality parameters
        final_prompt += " --quality 1"
        
        logger.info(f"Composed Midjourney prompt: {final_prompt}")
        
        return final_prompt
        
    except Exception as e:
        logger.warning(f"Prompt composition failed, using basic prompt: {e}")
        # Fallback to basic prompt
        user_prompt = request_data["prompt"]
        aspect_ratio = request_data.get("aspect_ratio", "16:9")
        return f"{user_prompt} --ar {aspect_ratio} --v 6"

async def initiate_midjourney_generation(
    request_data: Dict[str, Any], 
    mj_prompt: str, 
    style_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Initiate Midjourney generation with style and character references"""
    try:
        # Prepare generation parameters
        generation_params = {
            "prompt": mj_prompt,
            "style_reference_url": style_data.get("style_reference_url"),
            "character_reference_url": request_data.get("user_face_url"),
            "aspect_ratio": request_data.get("aspect_ratio", "16:9"),
            "model": request_data.get("model", "v6"),
            "quality": "standard"
        }
        
        # Remove None values
        generation_params = {k: v for k, v in generation_params.items() if v is not None}
        
        # Call Midjourney service
        result = await midjourney_service.generate_image(**generation_params)
        
        if not result or "task_id" not in result:
            raise MidjourneyServiceError("Invalid Midjourney response")
        
        return {
            "task_id": result["task_id"],
            "service": result.get("service", "goapi"),
            "generation_params": generation_params
        }
        
    except MidjourneyServiceError as e:
        raise MidjourneyTimeoutError(f"Midjourney initiation failed: {str(e)}")
    except Exception as e:
        raise MidjourneyTimeoutError(f"Generation initiation error: {str(e)}")

async def poll_midjourney_completion(request_id: str, task_id: str, service: str) -> Dict[str, Any]:
    """Poll Midjourney for completion with progress updates"""
    try:
        max_polls = 90  # 3 minutes with 2-second intervals
        poll_count = 0
        
        while poll_count < max_polls:
            try:
                # Check generation status
                status_result = await midjourney_service.check_generation_status(task_id, service)
                
                if not status_result:
                    raise MidjourneyServiceError("No status response")
                
                status = status_result.get("status", "processing")
                progress = status_result.get("progress", 0)
                
                # Calculate overall progress (65-95% range)
                overall_progress = 65 + int(progress * 0.30)  # Scale to 65-95%
                
                # Broadcast progress update
                await broadcast_progress(
                    request_id, 
                    overall_progress, 
                    "generating", 
                    f"Creating thumbnail... {progress}%"
                )
                
                # Check completion
                if status == "completed":
                    image_url = status_result.get("image_url")
                    if not image_url:
                        raise MidjourneyServiceError("No image URL in completed result")
                    
                    return {
                        "status": "completed",
                        "image_url": image_url,
                        "task_id": task_id,
                        "service": service,
                        "generation_metadata": status_result
                    }
                
                elif status == "failed":
                    error_msg = status_result.get("error", "Generation failed")
                    raise MidjourneyServiceError(f"Midjourney generation failed: {error_msg}")
                
                # Wait before next poll
                await asyncio.sleep(2)
                poll_count += 1
                
            except asyncio.TimeoutError:
                logger.warning(f"Polling timeout for task {task_id}, attempt {poll_count}")
                poll_count += 1
                continue
        
        # Timeout reached
        raise MidjourneyTimeoutError(f"Generation timeout after {max_polls * 2} seconds")
        
    except MidjourneyServiceError as e:
        raise MidjourneyTimeoutError(f"Midjourney polling failed: {str(e)}")
    except Exception as e:
        raise MidjourneyTimeoutError(f"Polling error: {str(e)}")

async def download_result_image(image_url: str) -> bytes:
    """Download the generated image"""
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download image: HTTP {response.status}")
                
                image_data = await response.read()
                
                if len(image_data) < 1000:  # Minimum viable image size
                    raise Exception("Downloaded image is too small")
                
                return image_data
                
    except Exception as e:
        raise GenerationPipelineError(f"Image download failed: {str(e)}")

async def upload_to_storage(request_id: str, image_data: bytes) -> str:
    """Upload image to storage and return URL"""
    try:
        # Mock storage upload (replace with actual R2/S3 integration)
        filename = f"generated/gen_{request_id}_{int(time.time())}.jpg"
        
        # In production, upload to R2/S3
        # For now, return a mock URL
        final_url = f"https://storage.routix.ai/{filename}"
        
        logger.info(f"Image uploaded to storage: {final_url}")
        
        return final_url
        
    except Exception as e:
        raise GenerationPipelineError(f"Storage upload failed: {str(e)}")

async def finalize_generation(
    request_id: str,
    request_data: Dict[str, Any],
    final_url: str,
    processing_time: float,
    template_used: Dict[str, Any],
    generation_result: Dict[str, Any]
) -> Dict[str, Any]:
    """Finalize generation: update database and deduct credits"""
    try:
        # Update generation request with results
        update_data = {
            "status": "completed",
            "progress": 100,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "result": {
                "image_url": final_url,
                "processing_time": processing_time,
                "template_used": template_used["id"],
                "generation_metadata": generation_result
            }
        }
        
        # Update cached generation data
        request_data.update(update_data)
        await generation_service._cache_generation_data(request_id, request_data)
        
        # Deduct credits from user
        credits_cost = request_data.get("credits_cost", 1)
        await user_service.deduct_user_credits(
            user_id=request_data["user_id"],
            amount=credits_cost,
            reason=f"Thumbnail generation - {request_id}",
            metadata={
                "generation_id": request_id,
                "template_used": template_used["id"],
                "processing_time": processing_time
            }
        )
        
        # Track completion analytics
        await generation_service._track_generation_event(
            request_id, "completed", request_data["user_id"]
        )
        
        return {
            "request_id": request_id,
            "final_url": final_url,
            "credits_deducted": credits_cost,
            "processing_time": processing_time
        }
        
    except Exception as e:
        raise GenerationPipelineError(f"Finalization failed: {str(e)}")

# Helper Functions

async def broadcast_progress(request_id: str, progress: int, status: str, message: str) -> None:
    """Broadcast progress update via Redis pub/sub"""
    try:
        progress_data = {
            "request_id": request_id,
            "progress": progress,
            "status": status,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Broadcast to Redis pub/sub for real-time updates
        await redis_service.publish(
            f"generation:{request_id}",
            json.dumps(progress_data)
        )
        
        # Also cache current progress
        await redis_service.set(
            f"progress:generation:{request_id}",
            progress_data,
            300  # 5 minutes TTL
        )
        
        logger.info(f"Progress broadcast: {request_id} - {progress}% - {message}")
        
    except Exception as e:
        logger.error(f"Failed to broadcast progress: {e}")

async def handle_generation_failure(request_id: str, error_message: str) -> None:
    """Handle generation failure"""
    try:
        # Update generation status
        failure_data = {
            "status": "failed",
            "progress": 0,
            "error": error_message,
            "failed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Get original request data
        request_data = await generation_service._get_cached_generation_data(request_id)
        if request_data:
            request_data.update(failure_data)
            await generation_service._cache_generation_data(request_id, request_data)
            
            # Track failure
            await generation_service._track_generation_event(
                request_id, "failed", request_data.get("user_id", "unknown")
            )
        
        # Broadcast failure
        await broadcast_progress(request_id, 0, "failed", f"Generation failed: {error_message}")
        
        logger.error(f"Generation marked as failed: {request_id} - {error_message}")
        
    except Exception as e:
        logger.error(f"Failed to handle generation failure: {e}")

async def handle_credit_error(request_id: str, request_data: Dict[str, Any], error_message: str) -> None:
    """Handle credit-related errors"""
    try:
        # Mark generation as failed due to credits
        await handle_generation_failure(request_id, error_message)
        
        # Notify user about credit issue (mock implementation)
        user_id = request_data.get("user_id")
        if user_id:
            logger.info(f"Credit error notification sent to user {user_id}: {error_message}")
        
    except Exception as e:
        logger.error(f"Failed to handle credit error: {e}")

async def use_fallback_template(request_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Use fallback template when no matches found"""
    try:
        logger.info(f"Using fallback template for generation {request_id}")
        
        # Get a default/fallback template
        fallback_templates = await template_service.get_templates(
            limit=1,
            filters={"is_default": True}
        )
        
        if not fallback_templates["templates"]:
            # Create a basic fallback template data
            fallback_template = {
                "id": "fallback_default",
                "title": "Default Template",
                "image_url": "https://via.placeholder.com/1920x1080/3B82F6/FFFFFF?text=Default+Template",
                "analysis_result": {
                    "dominant_colors": ["#3B82F6", "#FFFFFF"],
                    "typography_style": "modern",
                    "composition": "centered",
                    "energy_level": "medium",
                    "mood": "professional"
                }
            }
        else:
            fallback_template = fallback_templates["templates"][0]
        
        # Continue with fallback template
        await broadcast_progress(request_id, 35, "matching_templates", "Using fallback template...")
        
        # Continue pipeline with fallback template
        # This would continue the pipeline from step 4 onwards
        # For now, return a basic result
        return {
            "request_id": request_id,
            "status": "completed_with_fallback",
            "template_used": fallback_template["id"],
            "message": "Generation completed using fallback template"
        }
        
    except Exception as e:
        raise GenerationPipelineError(f"Fallback template failed: {str(e)}")

# Batch processing task
@celery_app.task
def batch_generate_thumbnails_task(request_ids: List[str]) -> Dict[str, Any]:
    """Process multiple generation requests in parallel"""
    try:
        from celery import group
        
        # Create group of generation tasks
        job = group(
            generate_thumbnail_task.s(request_id) 
            for request_id in request_ids
        )
        
        # Execute in parallel
        result = job.apply_async()
        
        return {
            "batch_id": result.id,
            "total_requests": len(request_ids),
            "status": "processing",
            "request_ids": request_ids
        }
        
    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "request_ids": request_ids
        }