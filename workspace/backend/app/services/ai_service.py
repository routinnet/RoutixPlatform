"""
Enhanced AI Services for Routix Platform
Handles Gemini Vision API, OpenAI GPT-4 Vision, and Embedding generation
"""
import json
import asyncio
import base64
import hashlib
from io import BytesIO
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import httpx
from PIL import Image
import google.generativeai as genai
import openai
from app.core.config import settings
from app.services.redis_service import redis_service

class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass

class EmbeddingService:
    """Enhanced embedding service with caching and batch processing"""
    
    def __init__(self):
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
            print("Warning: OPENAI_API_KEY not configured for embeddings")
        
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = settings.EMBEDDING_DIMENSIONS
        self.cache_ttl = settings.EMBEDDING_CACHE_TTL
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
        self.max_retries = 3
    
    async def generate_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding for text with Redis caching
        
        Args:
            text: Input text to embed
            use_cache: Whether to use Redis cache
            
        Returns:
            List of float values representing the embedding (1536 dimensions)
        """
        if not self.openai_client:
            raise AIServiceError("OpenAI client not configured for embeddings")
        
        if not text or not text.strip():
            raise AIServiceError("Empty text provided for embedding")
        
        # Create cache key
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        cache_key = f"embedding:{self.model}:{text_hash}"
        
        # Check cache first
        if use_cache:
            cached_embedding = await redis_service.get(cache_key)
            if cached_embedding and isinstance(cached_embedding, list):
                print(f"Retrieved cached embedding for text hash: {text_hash[:8]}...")
                return cached_embedding
        
        # Generate new embedding with retry logic
        for attempt in range(self.max_retries):
            try:
                print(f"Generating embedding (attempt {attempt + 1}) for text: {text[:50]}...")
                
                response = await asyncio.to_thread(
                    self.openai_client.embeddings.create,
                    model=self.model,
                    input=text,
                    encoding_format="float"
                )
                
                if not response.data or len(response.data) == 0:
                    raise AIServiceError("Empty embedding response from OpenAI")
                
                embedding = response.data[0].embedding
                
                # Validate embedding dimensions
                if len(embedding) != self.dimensions:
                    raise AIServiceError(f"Expected {self.dimensions} dimensions, got {len(embedding)}")
                
                # Cache the result
                if use_cache:
                    await redis_service.set(cache_key, embedding, self.cache_ttl)
                    print(f"Cached embedding for text hash: {text_hash[:8]}...")
                
                return embedding
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Embedding generation failed (attempt {attempt + 1}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise AIServiceError(f"Failed to generate embedding after {self.max_retries} attempts: {e}")
    
    async def generate_batch_embeddings(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with caching and batching
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use Redis cache
            
        Returns:
            List of embeddings in the same order as input texts
        """
        if not texts:
            return []
        
        if not self.openai_client:
            raise AIServiceError("OpenAI client not configured for embeddings")
        
        print(f"Processing batch of {len(texts)} texts for embeddings...")
        
        # Check cache for each text
        embeddings = [None] * len(texts)  # Initialize with None placeholders
        uncached_texts = []
        uncached_indices = []
        
        if use_cache:
            for i, text in enumerate(texts):
                if not text or not text.strip():
                    embeddings[i] = [0.0] * self.dimensions  # Zero vector for empty text
                    continue
                    
                text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
                cache_key = f"embedding:{self.model}:{text_hash}"
                cached_embedding = await redis_service.get(cache_key)
                
                if cached_embedding and isinstance(cached_embedding, list):
                    embeddings[i] = cached_embedding
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            # No caching, process all texts
            uncached_texts = [t for t in texts if t and t.strip()]
            uncached_indices = list(range(len(texts)))
        
        print(f"Found {len(texts) - len(uncached_texts)} cached embeddings, generating {len(uncached_texts)} new ones")
        
        # Generate embeddings for uncached texts in batches
        if uncached_texts:
            try:
                # Process in batches to respect API limits
                for batch_start in range(0, len(uncached_texts), self.batch_size):
                    batch_end = min(batch_start + self.batch_size, len(uncached_texts))
                    batch_texts = uncached_texts[batch_start:batch_end]
                    batch_indices = uncached_indices[batch_start:batch_end]
                    
                    print(f"Processing batch {batch_start//self.batch_size + 1}: {len(batch_texts)} texts")
                    
                    # Generate embeddings for this batch
                    for attempt in range(self.max_retries):
                        try:
                            response = await asyncio.to_thread(
                                self.openai_client.embeddings.create,
                                model=self.model,
                                input=batch_texts,
                                encoding_format="float"
                            )
                            
                            if not response.data or len(response.data) != len(batch_texts):
                                raise AIServiceError(f"Expected {len(batch_texts)} embeddings, got {len(response.data) if response.data else 0}")
                            
                            # Store embeddings and cache them
                            for i, embedding_data in enumerate(response.data):
                                embedding = embedding_data.embedding
                                
                                # Validate dimensions
                                if len(embedding) != self.dimensions:
                                    raise AIServiceError(f"Expected {self.dimensions} dimensions, got {len(embedding)}")
                                
                                original_index = batch_indices[i]
                                embeddings[original_index] = embedding
                                
                                # Cache the result
                                if use_cache:
                                    text = batch_texts[i]
                                    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
                                    cache_key = f"embedding:{self.model}:{text_hash}"
                                    await redis_service.set(cache_key, embedding, self.cache_ttl)
                            
                            break  # Success, exit retry loop
                            
                        except Exception as e:
                            if attempt < self.max_retries - 1:
                                wait_time = 2 ** attempt
                                print(f"Batch embedding failed (attempt {attempt + 1}): {e}")
                                print(f"Retrying in {wait_time} seconds...")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                raise AIServiceError(f"Batch embedding failed after {self.max_retries} attempts: {e}")
                    
                    # Small delay between batches to respect rate limits
                    if batch_end < len(uncached_texts):
                        await asyncio.sleep(0.1)
                
            except Exception as e:
                raise AIServiceError(f"Batch embedding generation failed: {e}")
        
        # Fill any remaining None values with zero vectors
        for i in range(len(embeddings)):
            if embeddings[i] is None:
                embeddings[i] = [0.0] * self.dimensions
        
        print(f"Batch embedding generation completed: {len(embeddings)} embeddings")
        return embeddings
    
    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding service statistics"""
        try:
            # Count cached embeddings
            cache_pattern = f"embedding:{self.model}:*"
            # Note: In production, you'd want to use SCAN instead of KEYS for large datasets
            
            stats = {
                "model": self.model,
                "dimensions": self.dimensions,
                "cache_ttl": self.cache_ttl,
                "batch_size": self.batch_size,
                "service_available": self.openai_client is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            return {
                "error": str(e),
                "service_available": False,
                "timestamp": datetime.utcnow().isoformat()
            }

class VisionAIService:
    """Vision AI service for template analysis"""
    
    def __init__(self):
        # Configure Gemini
        if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-pro-vision')
        else:
            self.gemini_model = None
            print("Warning: GEMINI_API_KEY not configured")
        
        # Configure OpenAI
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
            print("Warning: OPENAI_API_KEY not configured")
        
        self.max_retries = 3
        self.retry_delay = 1
    
    async def analyze_template_image(self, image_url: str, template_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze template image and extract design DNA
        
        Args:
            image_url: URL or path to the image
            template_id: Optional template ID for caching
            
        Returns:
            Dict containing design DNA analysis
        """
        try:
            # Check cache first
            if template_id:
                cache_key = f"template:analysis:{template_id}"
                cached_result = await redis_service.get(cache_key)
                if cached_result:
                    print(f"Returning cached analysis for template {template_id}")
                    return cached_result
            
            # Load and validate image
            image_data = await self._load_image(image_url)
            if not image_data:
                raise AIServiceError(f"Failed to load image from {image_url}")
            
            # Try Gemini first, fallback to OpenAI
            analysis_result = None
            
            if self.gemini_model:
                try:
                    print("Attempting analysis with Gemini Vision...")
                    analysis_result = await self._analyze_with_gemini(image_data)
                except Exception as e:
                    print(f"Gemini analysis failed: {e}")
                    analysis_result = None
            
            if not analysis_result and self.openai_client:
                try:
                    print("Falling back to OpenAI GPT-4 Vision...")
                    analysis_result = await self._analyze_with_openai(image_data)
                except Exception as e:
                    print(f"OpenAI analysis failed: {e}")
                    raise AIServiceError(f"Both AI services failed. Last error: {e}")
            
            if not analysis_result:
                raise AIServiceError("No AI service available for analysis")
            
            # Enhance and validate result
            enhanced_result = self._enhance_analysis_result(analysis_result, image_url)
            
            # Cache result
            if template_id:
                await redis_service.set(cache_key, enhanced_result, 86400)  # 24 hours
            
            return enhanced_result
            
        except Exception as e:
            print(f"Template analysis failed: {e}")
            raise AIServiceError(f"Template analysis failed: {str(e)}")
    
    async def _load_image(self, image_source: str) -> Optional[bytes]:
        """Load image from URL or file path"""
        try:
            if image_source.startswith(('http://', 'https://')):
                # Load from URL
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_source, timeout=30)
                    response.raise_for_status()
                    return response.content
            else:
                # Load from file path
                with open(image_source, 'rb') as f:
                    return f.read()
        except Exception as e:
            print(f"Failed to load image from {image_source}: {e}")
            return None
    
    async def _analyze_with_gemini(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image using Gemini Vision API"""
        try:
            # Convert to PIL Image for Gemini
            image = Image.open(BytesIO(image_data))
            
            # Prepare analysis prompt
            prompt = self._get_analysis_prompt()
            
            # Generate content with retry logic
            for attempt in range(self.max_retries):
                try:
                    response = await asyncio.to_thread(
                        self.gemini_model.generate_content,
                        [prompt, image]
                    )
                    
                    if response and response.text:
                        # Parse JSON response
                        result = json.loads(response.text.strip())
                        result['ai_provider'] = 'gemini'
                        return result
                    else:
                        raise AIServiceError("Empty response from Gemini")
                        
                except json.JSONDecodeError as e:
                    if attempt < self.max_retries - 1:
                        print(f"JSON parsing failed (attempt {attempt + 1}), retrying...")
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise AIServiceError(f"Failed to parse Gemini response as JSON: {e}")
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        print(f"Gemini API error (attempt {attempt + 1}): {e}")
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise AIServiceError(f"Gemini API failed after {self.max_retries} attempts: {e}")
            
        except Exception as e:
            raise AIServiceError(f"Gemini analysis error: {e}")
    
    async def _analyze_with_openai(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze image using OpenAI GPT-4 Vision API"""
        try:
            # Convert image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare analysis prompt
            prompt = self._get_analysis_prompt()
            
            # Generate content with retry logic
            for attempt in range(self.max_retries):
                try:
                    response = await asyncio.to_thread(
                        self.openai_client.chat.completions.create,
                        model="gpt-4-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}",
                                            "detail": "high"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=2000,
                        temperature=0.1
                    )
                    
                    if response.choices and response.choices[0].message.content:
                        content = response.choices[0].message.content.strip()
                        
                        # Extract JSON from response
                        if content.startswith('```json'):
                            content = content.replace('```json', '').replace('```', '').strip()
                        
                        result = json.loads(content)
                        result['ai_provider'] = 'openai'
                        return result
                    else:
                        raise AIServiceError("Empty response from OpenAI")
                        
                except json.JSONDecodeError as e:
                    if attempt < self.max_retries - 1:
                        print(f"JSON parsing failed (attempt {attempt + 1}), retrying...")
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise AIServiceError(f"Failed to parse OpenAI response as JSON: {e}")
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        print(f"OpenAI API error (attempt {attempt + 1}): {e}")
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise AIServiceError(f"OpenAI API failed after {self.max_retries} attempts: {e}")
            
        except Exception as e:
            raise AIServiceError(f"OpenAI analysis error: {e}")
    
    def _get_analysis_prompt(self) -> str:
        """Get the analysis prompt for AI models"""
        return """
Analyze this thumbnail design image and extract comprehensive design information. Return ONLY valid JSON with this exact structure:

{
  "color_analysis": {
    "primary_colors": ["#FF6B35", "#004E89", "#FFFFFF"],
    "secondary_colors": ["#FFE66D", "#A7C957"],
    "color_temperature": "warm",
    "contrast_level": "high"
  },
  "typography": {
    "text_style": "bold",
    "text_size": "large",
    "text_placement": "center",
    "font_characteristics": "sans-serif, modern"
  },
  "composition": {
    "layout_type": "centered",
    "focal_points": ["center", "top-right"],
    "visual_hierarchy": "clear",
    "balance": "symmetric"
  },
  "visual_elements": {
    "has_human_face": false,
    "has_text_overlay": true,
    "has_logo_branding": true,
    "background_type": "gradient",
    "visual_effects": ["glow", "shadow"]
  },
  "style_characteristics": {
    "design_style": "modern",
    "energy_level": 8,
    "mood": "exciting",
    "target_audience": "gaming"
  },
  "technical_details": {
    "image_quality": "high",
    "resolution_category": "standard",
    "aspect_ratio": "16:9"
  }
}

Requirements:
- energy_level: integer 1-10 (1=calm, 10=high-energy)
- color_temperature: "warm", "cool", or "neutral"
- contrast_level: "low", "medium", or "high"
- Return only valid JSON, no additional text
- Be accurate and specific in your analysis
"""
    
    def _enhance_analysis_result(self, analysis: Dict[str, Any], image_url: str) -> Dict[str, Any]:
        """Enhance analysis result with additional metadata"""
        enhanced = {
            **analysis,
            "metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "analysis_version": "1.0",
                "image_url": image_url,
                "ai_provider": analysis.get('ai_provider', 'unknown')
            }
        }
        
        # Generate searchable text for embeddings
        enhanced["searchable_text"] = self._generate_searchable_text(analysis)
        
        # Calculate confidence scores
        enhanced["confidence_scores"] = self._calculate_confidence_scores(analysis)
        
        return enhanced
    
    def _generate_searchable_text(self, analysis: Dict[str, Any]) -> str:
        """Generate searchable text from analysis for embeddings"""
        text_parts = []
        
        # Style characteristics
        if "style_characteristics" in analysis:
            style = analysis["style_characteristics"]
            text_parts.extend([
                style.get("design_style", ""),
                style.get("mood", ""),
                style.get("target_audience", "")
            ])
        
        # Color information
        if "color_analysis" in analysis:
            colors = analysis["color_analysis"]
            text_parts.extend([
                colors.get("color_temperature", ""),
                f"contrast {colors.get('contrast_level', '')}"
            ])
        
        # Composition
        if "composition" in analysis:
            comp = analysis["composition"]
            text_parts.extend([
                comp.get("layout_type", ""),
                comp.get("balance", "")
            ])
        
        # Visual elements
        if "visual_elements" in analysis:
            visual = analysis["visual_elements"]
            if visual.get("has_human_face"):
                text_parts.append("human face person")
            if visual.get("has_text_overlay"):
                text_parts.append("text overlay typography")
            if visual.get("has_logo_branding"):
                text_parts.append("logo branding")
            text_parts.append(visual.get("background_type", ""))
        
        # Typography
        if "typography" in analysis:
            typo = analysis["typography"]
            text_parts.extend([
                typo.get("text_style", ""),
                typo.get("font_characteristics", "")
            ])
        
        return " ".join(filter(None, text_parts))
    
    def _calculate_confidence_scores(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for different aspects"""
        scores = {}
        
        # Basic confidence based on completeness
        total_fields = 6  # Expected main sections
        present_fields = len([k for k in analysis.keys() if k in [
            'color_analysis', 'typography', 'composition', 
            'visual_elements', 'style_characteristics', 'technical_details'
        ]])
        
        scores['overall'] = present_fields / total_fields
        
        # Individual section confidence
        for section in ['color_analysis', 'typography', 'composition', 'visual_elements']:
            if section in analysis:
                section_data = analysis[section]
                if isinstance(section_data, dict):
                    scores[section] = min(1.0, len(section_data) / 4)  # Assume 4 expected fields per section
                else:
                    scores[section] = 0.5
            else:
                scores[section] = 0.0
        
        return scores

# Global service instances
vision_ai_service = VisionAIService()
embedding_service = EmbeddingService()