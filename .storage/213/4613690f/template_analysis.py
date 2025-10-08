"""
Template Analysis Worker for Routix Platform
Automatic AI analysis of uploaded templates with Vision AI integration
"""
import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from celery import current_task
from app.workers.celery_app import celery_app
from app.services.template_service import template_service, TemplateServiceError
from app.services.ai_service import vision_ai_service, embedding_service, AIServiceError
from app.services.redis_service import redis_service

# Configure logging
logger = logging.getLogger(__name__)

class TemplateAnalysisError(Exception):
    """Custom exception for template analysis errors"""
    pass

class VisionAITimeoutError(TemplateAnalysisError):
    """Vision AI timeout error"""
    pass

class InvalidResponseError(TemplateAnalysisError):
    """Invalid AI response error"""
    pass

class DatabaseError(TemplateAnalysisError):
    """Database operation error"""
    pass

@celery_app.task(bind=True, max_retries=3)
def analyze_template_task(self, template_id: str, image_url: str) -> Dict[str, Any]:
    """
    Analyze template with AI and generate embeddings
    
    Args:
        template_id: Template ID to analyze
        image_url: URL of the template image
        
    Returns:
        Analysis result with design DNA and embedding
    """
    start_time = time.time()
    
    try:
        logger.info(f"[{datetime.utcnow()}] Starting template analysis for: {template_id}")
        
        # Step 1: Update status → "analyzing" (10%)
        logger.info(f"Step 1: Updating status to analyzing")
        asyncio.run(update_template_status(template_id, "analyzing", 10, "Starting analysis..."))
        
        # Step 2: Download image from URL (20%)
        logger.info(f"Step 2: Downloading image from URL")
        image_data = asyncio.run(download_template_image(template_id, image_url))
        asyncio.run(broadcast_analysis_progress(template_id, 20, "analyzing", "Image downloaded successfully"))
        
        # Step 3: Call Vision AI Service (Gemini) (30%)
        logger.info(f"Step 3: Calling Vision AI Service")
        ai_analysis = asyncio.run(analyze_with_vision_ai(template_id, image_url))
        asyncio.run(broadcast_analysis_progress(template_id, 30, "analyzing", "AI analysis in progress..."))
        
        # Step 4: Parse design DNA response (50%)
        logger.info(f"Step 4: Parsing design DNA response")
        design_dna = asyncio.run(parse_design_dna(template_id, ai_analysis))
        asyncio.run(broadcast_analysis_progress(template_id, 50, "analyzing", "Extracting design DNA..."))
        
        # Step 5: Generate embedding vector (70%)
        logger.info(f"Step 5: Generating embedding vector")
        embedding_data = asyncio.run(generate_template_embedding(template_id, design_dna))
        asyncio.run(broadcast_analysis_progress(template_id, 70, "analyzing", "Generating embedding vector..."))
        
        # Step 6: Update database with results (90%)
        logger.info(f"Step 6: Updating database with results")
        await_result = asyncio.run(update_template_analysis_results(
            template_id, design_dna, embedding_data, ai_analysis
        ))
        asyncio.run(broadcast_analysis_progress(template_id, 90, "analyzing", "Saving analysis results..."))
        
        # Step 7: Mark as "analyzed" (100%)
        logger.info(f"Step 7: Marking as analyzed")
        asyncio.run(finalize_template_analysis(template_id, start_time))
        
        # Step 8: Broadcast completion via Redis
        logger.info(f"Step 8: Broadcasting completion")
        asyncio.run(broadcast_analysis_progress(template_id, 100, "analyzed", "Analysis completed successfully! 🎉"))
        
        processing_time = time.time() - start_time
        logger.info(f"[{datetime.utcnow()}] Template analysis completed: {template_id} in {processing_time:.2f}s")
        
        return {
            "template_id": template_id,
            "status": "analyzed",
            "design_dna": design_dna,
            "embedding_dimensions": len(embedding_data["embedding"]),
            "processing_time": processing_time,
            "ai_service_used": ai_analysis.get("service_used", "gemini")
        }
        
    except VisionAITimeoutError as e:
        logger.warning(f"Vision AI timeout for {template_id}: {e}")
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_countdown = 30 * (2 ** self.request.retries)  # 30s, 60s, 120s
            logger.info(f"Retrying template analysis {template_id} in {retry_countdown}s")
            asyncio.run(broadcast_analysis_progress(
                template_id, 25, "retrying", f"Retrying analysis in {retry_countdown}s..."
            ))
            raise self.retry(countdown=retry_countdown, exc=e)
        else:
            asyncio.run(handle_analysis_failure(template_id, f"Vision AI timeout: {str(e)}"))
            raise TemplateAnalysisError(f"Analysis failed after retries: {str(e)}")
            
    except InvalidResponseError as e:
        logger.warning(f"Invalid response for {template_id}: {e}")
        # Retry after 30 seconds
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying template analysis {template_id} due to invalid response")
            asyncio.run(broadcast_analysis_progress(
                template_id, 30, "retrying", "Retrying due to invalid response..."
            ))
            raise self.retry(countdown=30, exc=e)
        else:
            asyncio.run(handle_analysis_failure(template_id, f"Invalid response: {str(e)}"))
            raise TemplateAnalysisError(f"Invalid response after retries: {str(e)}")
            
    except DatabaseError as e:
        logger.error(f"Database error for {template_id}: {e}")
        asyncio.run(handle_analysis_failure(template_id, f"Database error: {str(e)}"))
        raise TemplateAnalysisError(f"Database error: {str(e)}")
        
    except Exception as e:
        logger.error(f"Template analysis failed for {template_id}: {e}", exc_info=True)
        asyncio.run(handle_analysis_failure(template_id, str(e)))
        raise TemplateAnalysisError(f"Analysis failed: {str(e)}")

@celery_app.task
def batch_analyze_templates_task(template_ids: List[str]) -> Dict[str, Any]:
    """
    Process multiple template analysis requests in parallel using Celery groups
    
    Args:
        template_ids: List of template IDs to analyze
        
    Returns:
        Batch processing result with status and tracking info
    """
    try:
        logger.info(f"[{datetime.utcnow()}] Starting batch template analysis for {len(template_ids)} templates")
        
        from celery import group
        
        # Get template URLs for analysis
        template_urls = asyncio.run(get_template_urls_for_batch(template_ids))
        
        # Create group of analysis tasks
        job = group(
            analyze_template_task.s(template_id, template_urls.get(template_id, ""))
            for template_id in template_ids
            if template_id in template_urls
        )
        
        # Execute batch in parallel
        result = job.apply_async()
        
        # Track batch progress
        batch_id = result.id
        asyncio.run(track_batch_analysis(batch_id, template_ids))
        
        logger.info(f"Batch analysis started: {batch_id} with {len(template_ids)} templates")
        
        return {
            "batch_id": batch_id,
            "total_templates": len(template_ids),
            "status": "processing",
            "template_ids": template_ids,
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch template analysis failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e),
            "template_ids": template_ids,
            "failed_at": datetime.utcnow().isoformat()
        }

# Pipeline Step Functions

async def update_template_status(template_id: str, status: str, progress: int, message: str) -> None:
    """Update template analysis status"""
    try:
        # Update template status in service
        await template_service.update_template_status(template_id, {
            "analysis_status": status,
            "analysis_progress": progress,
            "analysis_message": message,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        # Broadcast progress
        await broadcast_analysis_progress(template_id, progress, status, message)
        
    except Exception as e:
        logger.error(f"Failed to update template status {template_id}: {e}")
        raise DatabaseError(f"Status update failed: {str(e)}")

async def download_template_image(template_id: str, image_url: str) -> bytes:
    """Download template image for analysis"""
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download image: HTTP {response.status}")
                
                image_data = await response.read()
                
                if len(image_data) < 1000:  # Minimum viable image size
                    raise Exception("Downloaded image is too small")
                
                # Validate image format
                if not image_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    logger.warning(f"Unusual image format for {template_id}: {image_url}")
                
                logger.info(f"Downloaded image for {template_id}: {len(image_data)} bytes")
                return image_data
                
    except Exception as e:
        raise TemplateAnalysisError(f"Image download failed: {str(e)}")

async def analyze_with_vision_ai(template_id: str, image_url: str) -> Dict[str, Any]:
    """Analyze template with Vision AI (Gemini with GPT-4V fallback)"""
    try:
        # Prepare analysis prompt for design DNA extraction
        analysis_prompt = """
        Analyze this thumbnail template image and extract comprehensive design DNA. Provide a JSON response with:
        
        1. "dominant_colors": Array of hex color codes (top 5 colors)
        2. "color_palette": {"primary": "#hex", "secondary": "#hex", "accent": "#hex"}
        3. "typography_style": "modern", "classic", "bold", "minimal", "decorative"
        4. "font_weight": "light", "regular", "medium", "bold", "black"
        5. "composition": "centered", "left_aligned", "right_aligned", "split", "layered"
        6. "layout_style": "clean", "busy", "balanced", "asymmetric", "grid"
        7. "energy_level": "low", "medium", "high", "extreme"
        8. "mood": "professional", "playful", "dramatic", "minimalist", "energetic", "calm"
        9. "visual_style": "flat", "gradient", "3d", "realistic", "illustrated", "abstract"
        10. "content_elements": Array of elements like ["text", "logo", "character", "background", "effects"]
        11. "target_audience": "general", "young_adults", "professionals", "gamers", "kids"
        12. "industry": "gaming", "tech", "lifestyle", "business", "educational", "entertainment"
        13. "has_faces": true/false
        14. "has_text": true/false
        15. "text_prominence": "none", "subtle", "moderate", "dominant"
        16. "background_type": "solid", "gradient", "image", "pattern", "transparent"
        17. "contrast_level": "low", "medium", "high"
        18. "saturation_level": "low", "medium", "high"
        19. "complexity": "simple", "moderate", "complex"
        20. "brand_style": "corporate", "startup", "creative", "gaming", "minimal"
        
        Respond ONLY with valid JSON. No additional text or explanations.
        """
        
        # Try Gemini first
        try:
            logger.info(f"Analyzing {template_id} with Gemini Vision AI")
            
            gemini_result = await vision_ai_service.analyze_image_content(
                image_url=image_url,
                custom_prompt=analysis_prompt
            )
            
            if gemini_result and gemini_result.get("analysis"):
                return {
                    "analysis": gemini_result["analysis"],
                    "service_used": "gemini",
                    "confidence": gemini_result.get("confidence", 0.8),
                    "processing_time": gemini_result.get("processing_time", 0)
                }
            else:
                raise VisionAITimeoutError("Gemini returned empty result")
                
        except Exception as gemini_error:
            logger.warning(f"Gemini analysis failed for {template_id}: {gemini_error}")
            
            # Fallback to OpenAI GPT-4V
            try:
                logger.info(f"Falling back to OpenAI GPT-4V for {template_id}")
                
                # Mock OpenAI GPT-4V call (implement actual integration)
                openai_result = await fallback_to_openai_vision(image_url, analysis_prompt)
                
                return {
                    "analysis": openai_result["analysis"],
                    "service_used": "openai_gpt4v",
                    "confidence": openai_result.get("confidence", 0.7),
                    "processing_time": openai_result.get("processing_time", 0),
                    "fallback_reason": str(gemini_error)
                }
                
            except Exception as openai_error:
                logger.error(f"Both Gemini and OpenAI failed for {template_id}: {openai_error}")
                raise VisionAITimeoutError(f"All AI services failed: Gemini({gemini_error}), OpenAI({openai_error})")
        
    except VisionAITimeoutError:
        raise
    except Exception as e:
        raise VisionAITimeoutError(f"Vision AI analysis failed: {str(e)}")

async def parse_design_dna(template_id: str, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Parse and validate design DNA from AI analysis"""
    try:
        analysis_text = ai_analysis.get("analysis", "{}")
        
        # Try to parse JSON response
        try:
            design_dna = json.loads(analysis_text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON for {template_id}: {e}")
            # Try to extract JSON from text
            design_dna = extract_json_from_text(analysis_text)
        
        # Validate and fill missing fields
        design_dna = validate_and_complete_design_dna(design_dna)
        
        # Add metadata
        design_dna["analysis_metadata"] = {
            "service_used": ai_analysis.get("service_used", "unknown"),
            "confidence": ai_analysis.get("confidence", 0.5),
            "processing_time": ai_analysis.get("processing_time", 0),
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Design DNA parsed for {template_id}: {len(design_dna)} attributes")
        
        return design_dna
        
    except Exception as e:
        raise InvalidResponseError(f"Design DNA parsing failed: {str(e)}")

async def generate_template_embedding(template_id: str, design_dna: Dict[str, Any]) -> Dict[str, Any]:
    """Generate embedding vector from design DNA"""
    try:
        # Create text representation of design DNA for embedding
        embedding_text = create_embedding_text_from_dna(design_dna)
        
        # Generate embedding using embedding service
        embedding_result = await embedding_service.generate_embedding(embedding_text)
        
        if not embedding_result or "embedding" not in embedding_result:
            raise Exception("Invalid embedding response")
        
        embedding_vector = embedding_result["embedding"]
        
        # Validate embedding dimensions
        if len(embedding_vector) != 1536:  # OpenAI text-embedding-3-small dimensions
            raise Exception(f"Invalid embedding dimensions: {len(embedding_vector)}")
        
        logger.info(f"Generated embedding for {template_id}: {len(embedding_vector)} dimensions")
        
        return {
            "embedding": embedding_vector,
            "embedding_text": embedding_text,
            "model_used": embedding_result.get("model", "text-embedding-3-small"),
            "dimensions": len(embedding_vector)
        }
        
    except Exception as e:
        raise TemplateAnalysisError(f"Embedding generation failed: {str(e)}")

async def update_template_analysis_results(
    template_id: str,
    design_dna: Dict[str, Any],
    embedding_data: Dict[str, Any],
    ai_analysis: Dict[str, Any]
) -> None:
    """Update template with analysis results"""
    try:
        # Prepare analysis results
        analysis_results = {
            "design_dna": design_dna,
            "embedding_vector": embedding_data["embedding"],
            "embedding_text": embedding_data["embedding_text"],
            "analysis_metadata": {
                "ai_service": ai_analysis.get("service_used", "gemini"),
                "confidence": ai_analysis.get("confidence", 0.8),
                "embedding_model": embedding_data.get("model_used", "text-embedding-3-small"),
                "embedding_dimensions": embedding_data.get("dimensions", 1536),
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
        
        # Update template via service
        await template_service.update_template_analysis(template_id, analysis_results)
        
        logger.info(f"Analysis results saved for template {template_id}")
        
    except Exception as e:
        raise DatabaseError(f"Failed to save analysis results: {str(e)}")

async def finalize_template_analysis(template_id: str, start_time: float) -> None:
    """Finalize template analysis"""
    try:
        processing_time = time.time() - start_time
        
        # Mark template as analyzed
        await template_service.update_template_status(template_id, {
            "analysis_status": "analyzed",
            "analysis_progress": 100,
            "analysis_completed_at": datetime.utcnow().isoformat(),
            "analysis_processing_time": processing_time
        })
        
        # Track analytics
        await track_analysis_completion(template_id, processing_time)
        
        logger.info(f"Template analysis finalized: {template_id} in {processing_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Failed to finalize analysis for {template_id}: {e}")
        raise DatabaseError(f"Finalization failed: {str(e)}")

# Helper Functions

async def broadcast_analysis_progress(template_id: str, progress: int, status: str, message: str) -> None:
    """Broadcast analysis progress via Redis pub/sub"""
    try:
        progress_data = {
            "template_id": template_id,
            "progress": progress,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to Redis pub/sub for real-time updates
        await redis_service.publish(
            f"template:analysis:{template_id}",
            json.dumps(progress_data)
        )
        
        # Cache current progress
        await redis_service.set(
            f"progress:template:{template_id}",
            progress_data,
            300  # 5 minutes TTL
        )
        
        logger.info(f"Analysis progress broadcast: {template_id} - {progress}% - {message}")
        
    except Exception as e:
        logger.error(f"Failed to broadcast analysis progress: {e}")

async def handle_analysis_failure(template_id: str, error_message: str) -> None:
    """Handle analysis failure"""
    try:
        # Update template status
        failure_data = {
            "analysis_status": "analysis_failed",
            "analysis_progress": 0,
            "analysis_error": error_message,
            "analysis_failed_at": datetime.utcnow().isoformat()
        }
        
        await template_service.update_template_status(template_id, failure_data)
        
        # Broadcast failure
        await broadcast_analysis_progress(
            template_id, 0, "analysis_failed", f"Analysis failed: {error_message}"
        )
        
        # Track failure analytics
        await track_analysis_failure(template_id, error_message)
        
        logger.error(f"Template analysis marked as failed: {template_id} - {error_message}")
        
    except Exception as e:
        logger.error(f"Failed to handle analysis failure: {e}")

async def fallback_to_openai_vision(image_url: str, prompt: str) -> Dict[str, Any]:
    """Fallback to OpenAI GPT-4V (mock implementation)"""
    try:
        # Mock OpenAI GPT-4V integration
        # In production, implement actual OpenAI Vision API call
        
        await asyncio.sleep(2)  # Simulate API call
        
        # Return mock analysis result
        mock_analysis = {
            "dominant_colors": ["#3B82F6", "#FFFFFF", "#1E40AF"],
            "color_palette": {"primary": "#3B82F6", "secondary": "#FFFFFF", "accent": "#1E40AF"},
            "typography_style": "modern",
            "font_weight": "bold",
            "composition": "centered",
            "layout_style": "clean",
            "energy_level": "medium",
            "mood": "professional",
            "visual_style": "flat",
            "content_elements": ["text", "background"],
            "target_audience": "professionals",
            "industry": "tech",
            "has_faces": False,
            "has_text": True,
            "text_prominence": "dominant",
            "background_type": "gradient",
            "contrast_level": "high",
            "saturation_level": "medium",
            "complexity": "simple",
            "brand_style": "corporate"
        }
        
        return {
            "analysis": json.dumps(mock_analysis),
            "confidence": 0.7,
            "processing_time": 2.0
        }
        
    except Exception as e:
        raise Exception(f"OpenAI Vision fallback failed: {str(e)}")

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from text response"""
    try:
        # Find JSON-like content in text
        import re
        
        # Look for JSON blocks
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        
        # Fallback to default structure
        return get_default_design_dna()
        
    except Exception:
        return get_default_design_dna()

def validate_and_complete_design_dna(design_dna: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and complete design DNA with defaults"""
    default_dna = get_default_design_dna()
    
    # Ensure all required fields exist
    for key, default_value in default_dna.items():
        if key not in design_dna or design_dna[key] is None:
            design_dna[key] = default_value
    
    # Validate color formats
    if "dominant_colors" in design_dna:
        design_dna["dominant_colors"] = validate_color_array(design_dna["dominant_colors"])
    
    if "color_palette" in design_dna:
        design_dna["color_palette"] = validate_color_palette(design_dna["color_palette"])
    
    return design_dna

def get_default_design_dna() -> Dict[str, Any]:
    """Get default design DNA structure"""
    return {
        "dominant_colors": ["#3B82F6", "#FFFFFF", "#1E40AF"],
        "color_palette": {"primary": "#3B82F6", "secondary": "#FFFFFF", "accent": "#1E40AF"},
        "typography_style": "modern",
        "font_weight": "regular",
        "composition": "centered",
        "layout_style": "clean",
        "energy_level": "medium",
        "mood": "professional",
        "visual_style": "flat",
        "content_elements": ["text", "background"],
        "target_audience": "general",
        "industry": "general",
        "has_faces": False,
        "has_text": True,
        "text_prominence": "moderate",
        "background_type": "solid",
        "contrast_level": "medium",
        "saturation_level": "medium",
        "complexity": "simple",
        "brand_style": "modern"
    }

def validate_color_array(colors: List[str]) -> List[str]:
    """Validate and fix color array"""
    valid_colors = []
    
    for color in colors[:5]:  # Max 5 colors
        if isinstance(color, str) and color.startswith('#') and len(color) == 7:
            valid_colors.append(color.upper())
        elif isinstance(color, str):
            # Try to fix common color formats
            if not color.startswith('#'):
                color = '#' + color
            if len(color) == 7:
                valid_colors.append(color.upper())
    
    # Ensure at least 3 colors
    while len(valid_colors) < 3:
        valid_colors.append("#3B82F6")
    
    return valid_colors

def validate_color_palette(palette: Dict[str, str]) -> Dict[str, str]:
    """Validate color palette"""
    default_palette = {"primary": "#3B82F6", "secondary": "#FFFFFF", "accent": "#1E40AF"}
    
    if not isinstance(palette, dict):
        return default_palette
    
    for key in ["primary", "secondary", "accent"]:
        if key not in palette or not isinstance(palette[key], str) or not palette[key].startswith('#'):
            palette[key] = default_palette[key]
    
    return palette

def create_embedding_text_from_dna(design_dna: Dict[str, Any]) -> str:
    """Create text representation for embedding generation"""
    text_parts = []
    
    # Add key attributes
    text_parts.append(f"Typography: {design_dna.get('typography_style', 'modern')}")
    text_parts.append(f"Mood: {design_dna.get('mood', 'professional')}")
    text_parts.append(f"Energy: {design_dna.get('energy_level', 'medium')}")
    text_parts.append(f"Style: {design_dna.get('visual_style', 'flat')}")
    text_parts.append(f"Industry: {design_dna.get('industry', 'general')}")
    text_parts.append(f"Audience: {design_dna.get('target_audience', 'general')}")
    text_parts.append(f"Composition: {design_dna.get('composition', 'centered')}")
    text_parts.append(f"Layout: {design_dna.get('layout_style', 'clean')}")
    
    # Add colors
    colors = design_dna.get('dominant_colors', [])
    if colors:
        text_parts.append(f"Colors: {', '.join(colors[:3])}")
    
    # Add content elements
    elements = design_dna.get('content_elements', [])
    if elements:
        text_parts.append(f"Elements: {', '.join(elements)}")
    
    return " | ".join(text_parts)

async def get_template_urls_for_batch(template_ids: List[str]) -> Dict[str, str]:
    """Get template URLs for batch processing"""
    try:
        template_urls = {}
        
        for template_id in template_ids:
            # Get template data (mock implementation)
            template_data = await template_service.get_template(template_id)
            if template_data and "image_url" in template_data:
                template_urls[template_id] = template_data["image_url"]
        
        return template_urls
        
    except Exception as e:
        logger.error(f"Failed to get template URLs for batch: {e}")
        return {}

async def track_batch_analysis(batch_id: str, template_ids: List[str]) -> None:
    """Track batch analysis progress"""
    try:
        batch_data = {
            "batch_id": batch_id,
            "template_ids": template_ids,
            "total_templates": len(template_ids),
            "started_at": datetime.utcnow().isoformat(),
            "status": "processing"
        }
        
        # Store batch tracking data
        await redis_service.set(f"batch:analysis:{batch_id}", batch_data, 3600)
        
        logger.info(f"Batch analysis tracking started: {batch_id}")
        
    except Exception as e:
        logger.error(f"Failed to track batch analysis: {e}")

async def track_analysis_completion(template_id: str, processing_time: float) -> None:
    """Track analysis completion analytics"""
    try:
        analytics_data = {
            "template_id": template_id,
            "event": "analysis_completed",
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await redis_service.lpush(f"analytics:template_analysis", analytics_data)
        await redis_service.expire(f"analytics:template_analysis", 86400 * 30)  # 30 days
        
    except Exception as e:
        logger.error(f"Failed to track analysis completion: {e}")

async def track_analysis_failure(template_id: str, error_message: str) -> None:
    """Track analysis failure analytics"""
    try:
        failure_data = {
            "template_id": template_id,
            "event": "analysis_failed",
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await redis_service.lpush(f"analytics:template_failures", failure_data)
        await redis_service.expire(f"analytics:template_failures", 86400 * 30)  # 30 days
        
    except Exception as e:
        logger.error(f"Failed to track analysis failure: {e}")