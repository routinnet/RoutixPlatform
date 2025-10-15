"""
Midjourney Service for Routix Platform
Handles thumbnail generation via GoAPI.ai proxy service
"""
import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, timezone
import httpx
from app.core.config import settings
from app.services.redis_service import redis_service

import logging
logger = logging.getLogger(__name__)


class MidjourneyServiceError(Exception):
    """Custom exception for Midjourney service errors"""
    pass

class MidjourneyService:
    """Midjourney thumbnail generation service via GoAPI.ai"""
    
    def __init__(self):
        # GoAPI.ai configuration
        self.goapi_base_url = "https://api.goapi.ai/api/midjourney/v1"
        self.goapi_api_key = getattr(settings, 'GOAPI_API_KEY', None)
        
        # UseAPI.net fallback configuration
        self.useapi_base_url = "https://api.useapi.net/v1/midjourney"
        self.useapi_api_key = getattr(settings, 'USEAPI_API_KEY', None)
        
        # Service configuration
        self.max_retries = 3
        self.poll_interval = 10  # seconds
        self.max_poll_time = 600  # 10 minutes
        self.timeout = 30  # HTTP timeout
        
        # Midjourney parameters
        self.default_aspect_ratio = "16:9"
        self.default_model = "v6"
        self.default_stylize = 750
        
        if not self.goapi_api_key and not self.useapi_api_key:
            logger.info("Warning: Neither GOAPI_API_KEY nor USEAPI_API_KEY configured")
    
    async def generate_thumbnail(
        self,
        prompt: str,
        template_analysis: Optional[Dict[str, Any]] = None,
        user_face_url: Optional[str] = None,
        user_logo_url: Optional[str] = None,
        custom_text: Optional[str] = None,
        aspect_ratio: str = "16:9",
        model: str = "v6"
    ) -> Dict[str, Any]:
        """
        Generate thumbnail using Midjourney
        
        Args:
            prompt: Base generation prompt
            template_analysis: Analysis from Vision AI for style reference
            user_face_url: URL to user's face for character reference
            user_logo_url: URL to user's logo for branding
            custom_text: Custom text to include
            aspect_ratio: Image aspect ratio (16:9, 1:1, etc.)
            model: Midjourney model version
            
        Returns:
            Dict containing generation result and metadata
        """
        try:
            logger.info(f"Starting Midjourney generation...")
            
            # Build enhanced prompt
            enhanced_prompt = self._build_enhanced_prompt(
                prompt, template_analysis, custom_text, aspect_ratio, model
            )
            
            # Try GoAPI.ai first, fallback to UseAPI.net
            generation_result = None
            
            if self.goapi_api_key:
                try:
                    logger.info("Attempting generation with GoAPI.ai...")
                    generation_result = await self._generate_with_goapi(
                        enhanced_prompt, user_face_url, user_logo_url
                    )
                except Exception as e:
                    logger.info(f"GoAPI.ai generation failed: {e}")
                    generation_result = None
            
            if not generation_result and self.useapi_api_key:
                try:
                    logger.info("Falling back to UseAPI.net...")
                    generation_result = await self._generate_with_useapi(
                        enhanced_prompt, user_face_url, user_logo_url
                    )
                except Exception as e:
                    logger.info(f"UseAPI.net generation failed: {e}")
                    raise MidjourneyServiceError(f"Both Midjourney services failed. Last error: {e}")
            
            if not generation_result:
                raise MidjourneyServiceError("No Midjourney service available")
            
            # Enhance result with metadata
            enhanced_result = self._enhance_generation_result(
                generation_result, enhanced_prompt, template_analysis
            )
            
            logger.info(f"Midjourney generation completed successfully")
            return enhanced_result
            
        except Exception as e:
            logger.info(f"Midjourney generation failed: {e}")
            raise MidjourneyServiceError(f"Generation failed: {str(e)}")
    
    async def _generate_with_goapi(
        self,
        prompt: str,
        user_face_url: Optional[str] = None,
        user_logo_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate using GoAPI.ai service"""
        try:
            headers = {
                "Authorization": f"Bearer {self.goapi_api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request payload
            payload = {
                "prompt": prompt,
                "webhook_url": None,  # We'll poll instead
                "webhook_secret": None
            }
            
            # Add image references if provided
            if user_face_url:
                payload["image_url"] = user_face_url
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Submit generation request
                response = await client.post(
                    f"{self.goapi_base_url}/imagine",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                submit_result = response.json()
                task_id = submit_result.get("task_id")
                
                if not task_id:
                    raise MidjourneyServiceError("No task_id received from GoAPI.ai")
                
                logger.info(f"GoAPI.ai task submitted: {task_id}")
                
                # Poll for completion
                return await self._poll_goapi_status(task_id, headers)
                
        except Exception as e:
            raise MidjourneyServiceError(f"GoAPI.ai generation error: {e}")
    
    async def _generate_with_useapi(
        self,
        prompt: str,
        user_face_url: Optional[str] = None,
        user_logo_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate using UseAPI.net service"""
        try:
            headers = {
                "Authorization": f"Bearer {self.useapi_api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request payload
            payload = {
                "prompt": prompt,
                "webhook_url": None
            }
            
            # Add image references if provided
            if user_face_url:
                payload["image_url"] = user_face_url
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Submit generation request
                response = await client.post(
                    f"{self.useapi_base_url}/imagine",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                submit_result = response.json()
                job_id = submit_result.get("job_id") or submit_result.get("id")
                
                if not job_id:
                    raise MidjourneyServiceError("No job_id received from UseAPI.net")
                
                logger.info(f"UseAPI.net job submitted: {job_id}")
                
                # Poll for completion
                return await self._poll_useapi_status(job_id, headers)
                
        except Exception as e:
            raise MidjourneyServiceError(f"UseAPI.net generation error: {e}")
    
    async def _poll_goapi_status(self, task_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Poll GoAPI.ai for task completion"""
        start_time = time.time()
        poll_count = 0
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while time.time() - start_time < self.max_poll_time:
                poll_count += 1
                
                try:
                    response = await client.get(
                        f"{self.goapi_base_url}/task/{task_id}",
                        headers=headers
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    status = result.get("status", "").lower()
                    
                    logger.info(f"GoAPI.ai poll {poll_count}: {status}")
                    
                    if status in ["completed", "success"]:
                        image_url = result.get("image_url") or result.get("result", {}).get("image_url")
                        if image_url:
                            return {
                                "status": "completed",
                                "image_url": image_url,
                                "task_id": task_id,
                                "service": "goapi",
                                "poll_count": poll_count,
                                "generation_time": time.time() - start_time
                            }
                        else:
                            raise MidjourneyServiceError("Completed but no image URL received")
                    
                    elif status in ["failed", "error"]:
                        error_msg = result.get("error", "Unknown error")
                        raise MidjourneyServiceError(f"Generation failed: {error_msg}")
                    
                    elif status in ["pending", "processing", "in_progress"]:
                        # Continue polling with exponential backoff
                        wait_time = min(self.poll_interval * (1.5 ** min(poll_count - 1, 5)), 60)
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        logger.info(f"Unknown status: {status}, continuing...")
                        await asyncio.sleep(self.poll_interval)
                        continue
                
                except httpx.HTTPError as e:
                    if poll_count >= self.max_retries:
                        raise MidjourneyServiceError(f"Polling failed after {self.max_retries} retries: {e}")
                    
                    wait_time = self.poll_interval * (2 ** (poll_count - 1))
                    logger.info(f"Poll error, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                    continue
        
        raise MidjourneyServiceError(f"Generation timeout after {self.max_poll_time} seconds")
    
    async def _poll_useapi_status(self, job_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Poll UseAPI.net for job completion"""
        start_time = time.time()
        poll_count = 0
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while time.time() - start_time < self.max_poll_time:
                poll_count += 1
                
                try:
                    response = await client.get(
                        f"{self.useapi_base_url}/jobs/{job_id}",
                        headers=headers
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    status = result.get("status", "").lower()
                    
                    logger.info(f"UseAPI.net poll {poll_count}: {status}")
                    
                    if status in ["completed", "success"]:
                        image_url = result.get("image_url") or result.get("attachments", [{}])[0].get("url")
                        if image_url:
                            return {
                                "status": "completed",
                                "image_url": image_url,
                                "job_id": job_id,
                                "service": "useapi",
                                "poll_count": poll_count,
                                "generation_time": time.time() - start_time
                            }
                        else:
                            raise MidjourneyServiceError("Completed but no image URL received")
                    
                    elif status in ["failed", "error"]:
                        error_msg = result.get("error", "Unknown error")
                        raise MidjourneyServiceError(f"Generation failed: {error_msg}")
                    
                    elif status in ["pending", "processing", "in_progress", "queued"]:
                        # Continue polling with exponential backoff
                        wait_time = min(self.poll_interval * (1.5 ** min(poll_count - 1, 5)), 60)
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        logger.info(f"Unknown status: {status}, continuing...")
                        await asyncio.sleep(self.poll_interval)
                        continue
                
                except httpx.HTTPError as e:
                    if poll_count >= self.max_retries:
                        raise MidjourneyServiceError(f"Polling failed after {self.max_retries} retries: {e}")
                    
                    wait_time = self.poll_interval * (2 ** (poll_count - 1))
                    logger.info(f"Poll error, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                    continue
        
        raise MidjourneyServiceError(f"Generation timeout after {self.max_poll_time} seconds")
    
    def _build_enhanced_prompt(
        self,
        base_prompt: str,
        template_analysis: Optional[Dict[str, Any]] = None,
        custom_text: Optional[str] = None,
        aspect_ratio: str = "16:9",
        model: str = "v6"
    ) -> str:
        """Build enhanced Midjourney prompt with style references"""
        
        prompt_parts = [base_prompt]
        
        # Add custom text if provided
        if custom_text and custom_text.strip():
            prompt_parts.append(f'with text "{custom_text}"')
        
        # Add style characteristics from template analysis
        if template_analysis:
            style_parts = []
            
            # Extract style characteristics
            style_chars = template_analysis.get("style_characteristics", {})
            if style_chars:
                design_style = style_chars.get("design_style")
                mood = style_chars.get("mood")
                energy_level = style_chars.get("energy_level", 5)
                
                if design_style:
                    style_parts.append(f"{design_style} style")
                if mood:
                    style_parts.append(f"{mood} mood")
                
                # Convert energy level to descriptive terms
                if energy_level >= 8:
                    style_parts.append("high energy, dynamic")
                elif energy_level >= 6:
                    style_parts.append("energetic, vibrant")
                elif energy_level >= 4:
                    style_parts.append("balanced energy")
                else:
                    style_parts.append("calm, peaceful")
            
            # Extract color information
            color_analysis = template_analysis.get("color_analysis", {})
            if color_analysis:
                color_temp = color_analysis.get("color_temperature")
                contrast = color_analysis.get("contrast_level")
                
                if color_temp:
                    style_parts.append(f"{color_temp} colors")
                if contrast:
                    style_parts.append(f"{contrast} contrast")
            
            # Extract composition info
            composition = template_analysis.get("composition", {})
            if composition:
                layout = composition.get("layout_type")
                if layout:
                    style_parts.append(f"{layout} composition")
            
            if style_parts:
                prompt_parts.append(", ".join(style_parts))
        
        # Build final prompt
        enhanced_prompt = ", ".join(prompt_parts)
        
        # Add Midjourney parameters
        mj_params = []
        
        # Aspect ratio
        if aspect_ratio and aspect_ratio != "1:1":
            mj_params.append(f"--ar {aspect_ratio}")
        
        # Model version
        if model and model != "v6":
            mj_params.append(f"--{model}")
        
        # Stylize parameter
        mj_params.append(f"--stylize {self.default_stylize}")
        
        # Quality and style
        mj_params.append("--style raw")
        
        if mj_params:
            enhanced_prompt += " " + " ".join(mj_params)
        
        logger.info(f"Enhanced Midjourney prompt: {enhanced_prompt}")
        return enhanced_prompt
    
    def _enhance_generation_result(
        self,
        result: Dict[str, Any],
        prompt: str,
        template_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Enhance generation result with metadata"""
        
        enhanced = {
            **result,
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "service_version": "1.0",
                "prompt_used": prompt,
                "midjourney_service": result.get("service", "unknown")
            }
        }
        
        # Add template analysis reference
        if template_analysis:
            enhanced["metadata"]["template_analysis_used"] = True
            enhanced["metadata"]["style_reference"] = {
                "design_style": template_analysis.get("style_characteristics", {}).get("design_style"),
                "energy_level": template_analysis.get("style_characteristics", {}).get("energy_level"),
                "mood": template_analysis.get("style_characteristics", {}).get("mood")
            }
        else:
            enhanced["metadata"]["template_analysis_used"] = False
        
        # Calculate quality score based on generation time and poll count
        generation_time = result.get("generation_time", 0)
        poll_count = result.get("poll_count", 1)
        
        # Lower generation time and fewer polls indicate better performance
        quality_score = max(0.5, min(1.0, 1.0 - (generation_time / 300) - (poll_count / 20)))
        enhanced["metadata"]["quality_score"] = round(quality_score, 2)
        
        return enhanced
    
    async def upscale_image(
        self,
        task_id: str,
        upscale_index: int = 1,
        service: str = "goapi"
    ) -> Dict[str, Any]:
        """
        Upscale a generated image
        
        Args:
            task_id: Original generation task ID
            upscale_index: Which image to upscale (1-4)
            service: Which service was used for original generation
            
        Returns:
            Dict containing upscaled image result
        """
        try:
            logger.info(f"Starting image upscale...")
            
            if service == "goapi" and self.goapi_api_key:
                return await self._upscale_with_goapi(task_id, upscale_index)
            elif service == "useapi" and self.useapi_api_key:
                return await self._upscale_with_useapi(task_id, upscale_index)
            else:
                raise MidjourneyServiceError(f"Upscale not available for service: {service}")
                
        except Exception as e:
            logger.info(f"Image upscale failed: {e}")
            raise MidjourneyServiceError(f"Upscale failed: {str(e)}")
    
    async def _upscale_with_goapi(self, task_id: str, upscale_index: int) -> Dict[str, Any]:
        """Upscale using GoAPI.ai"""
        headers = {
            "Authorization": f"Bearer {self.goapi_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "task_id": task_id,
            "action": f"U{upscale_index}"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.goapi_base_url}/action",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            new_task_id = result.get("task_id")
            
            if not new_task_id:
                raise MidjourneyServiceError("No task_id received for upscale")
            
            # Poll for upscale completion
            return await self._poll_goapi_status(new_task_id, headers)
    
    async def _upscale_with_useapi(self, job_id: str, upscale_index: int) -> Dict[str, Any]:
        """Upscale using UseAPI.net"""
        headers = {
            "Authorization": f"Bearer {self.useapi_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "job_id": job_id,
            "action": f"upscale_{upscale_index}"
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.useapi_base_url}/action",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            new_job_id = result.get("job_id") or result.get("id")
            
            if not new_job_id:
                raise MidjourneyServiceError("No job_id received for upscale")
            
            # Poll for upscale completion
            return await self._poll_useapi_status(new_job_id, headers)
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get Midjourney service statistics"""
        try:
            stats = {
                "goapi_available": self.goapi_api_key is not None,
                "useapi_available": self.useapi_api_key is not None,
                "poll_interval": self.poll_interval,
                "max_poll_time": self.max_poll_time,
                "default_model": self.default_model,
                "default_aspect_ratio": self.default_aspect_ratio,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return stats
            
        except Exception as e:
            return {
                "error": str(e),
                "service_available": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

# Global Midjourney service instance
midjourney_service = MidjourneyService()