"""
Embedding service for generating vector embeddings
"""
import asyncio
import hashlib
from typing import List, Optional, Dict, Any
import openai
from app.core.config import settings
from app.services.redis_service import redis_service

import logging
logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
            logger.warning("OPENAI_API_KEY not configured for embeddings")
        
        self.model = "text-embedding-3-small"
        self.max_retries = 3
    
    async def generate_embedding(self, text: str, cache_ttl: int = 86400) -> List[float]:
        """
        Generate embedding for text with caching
        
        Args:
            text: Input text to embed
            cache_ttl: Cache time-to-live in seconds
            
        Returns:
            List of float values representing the embedding
        """
        if not self.openai_client:
            raise Exception("OpenAI client not configured")
        
        # Create cache key
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"embedding:{self.model}:{text_hash}"
        
        # Check cache first
        cached_embedding = await redis_service.get(cache_key)
        if cached_embedding:
            return cached_embedding
        
        # Generate new embedding
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.to_thread(
                    self.openai_client.embeddings.create,
                    model=self.model,
                    input=text,
                    encoding_format="float"
                )
                
                embedding = response.data[0].embedding
                
                # Cache the result
                await redis_service.set(cache_key, embedding, cache_ttl)
                
                return embedding
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.info(f"Embedding generation failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
                else:
                    raise Exception(f"Failed to generate embedding after {self.max_retries} attempts: {e}")
    
    async def generate_batch_embeddings(self, texts: List[str], cache_ttl: int = 86400) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            cache_ttl: Cache time-to-live in seconds
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        # Check cache for each text
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_key = f"embedding:{self.model}:{text_hash}"
            cached_embedding = await redis_service.get(cache_key)
            
            if cached_embedding:
                embeddings.append(cached_embedding)
            else:
                embeddings.append(None)  # Placeholder
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            try:
                response = await asyncio.to_thread(
                    self.openai_client.embeddings.create,
                    model=self.model,
                    input=uncached_texts,
                    encoding_format="float"
                )
                
                # Cache and store results
                for i, embedding_data in enumerate(response.data):
                    embedding = embedding_data.embedding
                    original_index = uncached_indices[i]
                    embeddings[original_index] = embedding
                    
                    # Cache the result
                    text = uncached_texts[i]
                    text_hash = hashlib.md5(text.encode()).hexdigest()
                    cache_key = f"embedding:{self.model}:{text_hash}"
                    await redis_service.set(cache_key, embedding, cache_ttl)
                
            except Exception as e:
                raise Exception(f"Batch embedding generation failed: {e}")
        
        return embeddings

# Global embedding service instance
embedding_service = EmbeddingService()
