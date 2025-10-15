"""
Template Service for Routix Platform
Handles template upload, AI analysis, vector search, and CRUD operations
"""
import asyncio
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import aiofiles
from PIL import Image
import httpx
from app.core.config import settings
from app.services.ai_service import vision_ai_service, embedding_service, AIServiceError
from app.services.redis_service import redis_service
from app.workers.ai_tasks import analyze_template_task

import logging
logger = logging.getLogger(__name__)


class TemplateServiceError(Exception):
    """Custom exception for template service errors"""
    pass

class TemplateService:
    """Comprehensive template management service"""
    
    def __init__(self):
        # File handling configuration
        self.upload_dir = Path("/workspace/backend/uploads/templates")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_IMAGE_EXTENSIONS
        
        # AI analysis configuration
        self.similarity_threshold = 0.85
        self.batch_size = 50
        self.cache_ttl = 86400  # 24 hours
        
        # Performance tracking
        self.analytics_enabled = True
        
    async def upload_template(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        auto_analyze: bool = True
    ) -> Dict[str, Any]:
        """
        Upload and process a new template
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            user_id: ID of uploading user
            title: Template title
            description: Optional description
            category: Template category
            tags: List of tags
            auto_analyze: Whether to run AI analysis automatically
            
        Returns:
            Dict containing template data and analysis results
        """
        try:
            logger.info(f"Starting template upload: {filename}")
            
            # Validate file
            await self._validate_file(file_content, filename)
            
            # Generate unique template ID
            template_id = self._generate_template_id(user_id, filename)
            
            # Save file
            file_path = await self._save_file(file_content, template_id, filename)
            
            # Create template metadata
            template_data = {
                "id": template_id,
                "user_id": user_id,
                "title": title,
                "description": description or "",
                "category": category or "uncategorized",
                "tags": tags or [],
                "filename": filename,
                "file_path": str(file_path),
                "file_size": len(file_content),
                "status": "uploaded",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "analysis_status": "pending" if auto_analyze else "skipped",
                "view_count": 0,
                "download_count": 0,
                "like_count": 0
            }
            
            # Cache template data
            await self._cache_template_data(template_id, template_data)
            
            # Queue AI analysis if requested
            analysis_task_id = None
            if auto_analyze:
                try:
                    # Get file URL for analysis
                    file_url = f"file://{file_path}"
                    
                    # Queue analysis task
                    task = analyze_template_task.delay(template_id, file_url)
                    analysis_task_id = task.id
                    
                    template_data["analysis_task_id"] = analysis_task_id
                    template_data["analysis_status"] = "processing"
                    
                    logger.info(f"AI analysis queued for template {template_id}: {analysis_task_id}")
                    
                except Exception as e:
                    logger.info(f"Failed to queue AI analysis: {e}")
                    template_data["analysis_status"] = "failed"
                    template_data["analysis_error"] = str(e)
            
            # Update cache with analysis info
            await self._cache_template_data(template_id, template_data)
            
            # Track upload analytics
            if self.analytics_enabled:
                await self._track_template_event(template_id, "uploaded", user_id)
            
            logger.info(f"Template upload completed: {template_id}")
            
            return {
                "template": template_data,
                "analysis_task_id": analysis_task_id,
                "message": "Template uploaded successfully"
            }
            
        except Exception as e:
            logger.info(f"Template upload failed: {e}")
            raise TemplateServiceError(f"Upload failed: {str(e)}")
    
    async def get_template(self, template_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get template by ID with analytics tracking
        
        Args:
            template_id: Template ID
            user_id: Optional user ID for analytics
            
        Returns:
            Template data with analysis results
        """
        try:
            # Get template data from cache
            template_data = await self._get_cached_template_data(template_id)
            
            if not template_data:
                raise TemplateServiceError(f"Template not found: {template_id}")
            
            # Get analysis results if available
            analysis_data = await self._get_template_analysis(template_id)
            if analysis_data:
                template_data["analysis"] = analysis_data
            
            # Track view analytics
            if self.analytics_enabled and user_id:
                await self._track_template_event(template_id, "viewed", user_id)
                template_data["view_count"] = template_data.get("view_count", 0) + 1
                await self._cache_template_data(template_id, template_data)
            
            return template_data
            
        except Exception as e:
            logger.info(f"Failed to get template {template_id}: {e}")
            raise TemplateServiceError(f"Failed to get template: {str(e)}")
    
    async def search_templates(
        self,
        query: Optional[str] = None,
        embedding: Optional[List[float]] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        limit: int = 20,
        similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Search templates using vector similarity and filters
        
        Args:
            query: Text query for semantic search
            embedding: Pre-computed embedding for similarity search
            category: Filter by category
            tags: Filter by tags
            user_id: Filter by user
            limit: Maximum results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            Search results with similarity scores
        """
        try:
            logger.info(f"Starting template search")
            
            results = []
            
            # Vector similarity search
            if query or embedding:
                vector_results = await self._vector_search(
                    query, embedding, limit * 2, similarity_threshold
                )
                results.extend(vector_results)
            
            # Filter-based search
            filter_results = await self._filter_search(category, tags, user_id, limit * 2)
            
            # Combine and deduplicate results
            combined_results = self._combine_search_results(results, filter_results)
            
            # Apply final filters and sorting
            filtered_results = self._apply_search_filters(
                combined_results, category, tags, user_id
            )
            
            # Limit results
            final_results = filtered_results[:limit]
            
            # Enhance results with metadata
            enhanced_results = await self._enhance_search_results(final_results)
            
            search_metadata = {
                "query": query,
                "total_found": len(filtered_results),
                "returned": len(final_results),
                "similarity_threshold": similarity_threshold,
                "search_time": datetime.now(timezone.utc).isoformat()
            }
            
            return {
                "results": enhanced_results,
                "metadata": search_metadata
            }
            
        except Exception as e:
            logger.info(f"Template search failed: {e}")
            raise TemplateServiceError(f"Search failed: {str(e)}")
    
    async def update_template(
        self,
        template_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update template metadata
        
        Args:
            template_id: Template ID
            user_id: User making the update
            updates: Fields to update
            
        Returns:
            Updated template data
        """
        try:
            # Get existing template
            template_data = await self._get_cached_template_data(template_id)
            
            if not template_data:
                raise TemplateServiceError(f"Template not found: {template_id}")
            
            # Check ownership (in production, add proper auth)
            if template_data.get("user_id") != user_id:
                raise TemplateServiceError("Unauthorized to update this template")
            
            # Apply updates
            allowed_fields = ["title", "description", "category", "tags"]
            for field in allowed_fields:
                if field in updates:
                    template_data[field] = updates[field]
            
            template_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Update cache
            await self._cache_template_data(template_id, template_data)
            
            # Track update analytics
            if self.analytics_enabled:
                await self._track_template_event(template_id, "updated", user_id)
            
            return template_data
            
        except Exception as e:
            logger.info(f"Failed to update template {template_id}: {e}")
            raise TemplateServiceError(f"Update failed: {str(e)}")
    
    async def delete_template(
        self,
        template_id: str,
        user_id: str,
        soft_delete: bool = True
    ) -> Dict[str, Any]:
        """
        Delete template (soft delete by default)
        
        Args:
            template_id: Template ID
            user_id: User requesting deletion
            soft_delete: Whether to soft delete (mark as deleted) or hard delete
            
        Returns:
            Deletion result
        """
        try:
            # Get existing template
            template_data = await self._get_cached_template_data(template_id)
            
            if not template_data:
                raise TemplateServiceError(f"Template not found: {template_id}")
            
            # Check ownership (in production, add proper auth)
            if template_data.get("user_id") != user_id:
                raise TemplateServiceError("Unauthorized to delete this template")
            
            if soft_delete:
                # Soft delete - mark as deleted
                template_data["status"] = "deleted"
                template_data["deleted_at"] = datetime.now(timezone.utc).isoformat()
                template_data["deleted_by"] = user_id
                
                await self._cache_template_data(template_id, template_data)
                
                result = {
                    "template_id": template_id,
                    "action": "soft_deleted",
                    "deleted_at": template_data["deleted_at"]
                }
            else:
                # Hard delete - remove files and cache
                file_path = template_data.get("file_path")
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                
                # Remove from cache
                await redis_service.delete(f"template:{template_id}")
                await redis_service.delete(f"template:analysis:{template_id}")
                
                result = {
                    "template_id": template_id,
                    "action": "hard_deleted",
                    "deleted_at": datetime.now(timezone.utc).isoformat()
                }
            
            # Track deletion analytics
            if self.analytics_enabled:
                await self._track_template_event(template_id, "deleted", user_id)
            
            return result
            
        except Exception as e:
            logger.info(f"Failed to delete template {template_id}: {e}")
            raise TemplateServiceError(f"Deletion failed: {str(e)}")
    
    async def get_popular_templates(
        self,
        timeframe: str = "week",
        category: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get popular templates based on analytics
        
        Args:
            timeframe: Time period (day, week, month, all)
            category: Optional category filter
            limit: Maximum results
            
        Returns:
            Popular templates with metrics
        """
        try:
            # Calculate time range
            now = datetime.now(timezone.utc)
            if timeframe == "day":
                start_time = now - timedelta(days=1)
            elif timeframe == "week":
                start_time = now - timedelta(weeks=1)
            elif timeframe == "month":
                start_time = now - timedelta(days=30)
            else:  # all
                start_time = datetime(2020, 1, 1)
            
            # Get analytics data (mock implementation)
            popular_templates = await self._get_popular_templates_from_analytics(
                start_time, category, limit
            )
            
            # Enhance with template data
            enhanced_results = []
            for template_info in popular_templates:
                template_data = await self._get_cached_template_data(template_info["template_id"])
                if template_data and template_data.get("status") != "deleted":
                    template_data["popularity_metrics"] = template_info["metrics"]
                    enhanced_results.append(template_data)
            
            return {
                "templates": enhanced_results,
                "timeframe": timeframe,
                "category": category,
                "total_found": len(enhanced_results)
            }
            
        except Exception as e:
            logger.info(f"Failed to get popular templates: {e}")
            raise TemplateServiceError(f"Failed to get popular templates: {str(e)}")
    
    async def batch_process_templates(
        self,
        template_ids: List[str],
        operation: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process multiple templates in batch
        
        Args:
            template_ids: List of template IDs
            operation: Operation to perform (analyze, reindex, etc.)
            parameters: Operation-specific parameters
            
        Returns:
            Batch processing results
        """
        try:
            logger.info(f"Starting batch operation '{operation}' on {len(template_ids)} templates")
            
            results = []
            
            if operation == "analyze":
                # Batch AI analysis
                for template_id in template_ids:
                    try:
                        template_data = await self._get_cached_template_data(template_id)
                        if template_data:
                            file_path = template_data.get("file_path")
                            if file_path:
                                task = analyze_template_task.delay(template_id, f"file://{file_path}")
                                results.append({
                                    "template_id": template_id,
                                    "status": "queued",
                                    "task_id": task.id
                                })
                            else:
                                results.append({
                                    "template_id": template_id,
                                    "status": "failed",
                                    "error": "No file path found"
                                })
                        else:
                            results.append({
                                "template_id": template_id,
                                "status": "failed",
                                "error": "Template not found"
                            })
                    except Exception as e:
                        results.append({
                            "template_id": template_id,
                            "status": "failed",
                            "error": str(e)
                        })
            
            elif operation == "reindex":
                # Batch reindexing for search
                for template_id in template_ids:
                    try:
                        analysis_data = await self._get_template_analysis(template_id)
                        if analysis_data and analysis_data.get("searchable_text"):
                            embedding = await embedding_service.generate_embedding(
                                analysis_data["searchable_text"]
                            )
                            # Store embedding (in production, update database)
                            await redis_service.set(
                                f"template:embedding:{template_id}",
                                embedding,
                                self.cache_ttl
                            )
                            results.append({
                                "template_id": template_id,
                                "status": "reindexed"
                            })
                        else:
                            results.append({
                                "template_id": template_id,
                                "status": "skipped",
                                "reason": "No analysis data"
                            })
                    except Exception as e:
                        results.append({
                            "template_id": template_id,
                            "status": "failed",
                            "error": str(e)
                        })
            
            else:
                raise TemplateServiceError(f"Unknown batch operation: {operation}")
            
            batch_summary = {
                "operation": operation,
                "total_templates": len(template_ids),
                "successful": len([r for r in results if r["status"] in ["queued", "reindexed"]]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Batch operation completed: {batch_summary['successful']}/{len(template_ids)} successful")
            
            return batch_summary
            
        except Exception as e:
            logger.info(f"Batch processing failed: {e}")
            raise TemplateServiceError(f"Batch processing failed: {str(e)}")
    
    # Private helper methods
    
    async def _validate_file(self, file_content: bytes, filename: str) -> None:
        """Validate uploaded file"""
        # Check file size
        if len(file_content) > self.max_file_size:
            raise TemplateServiceError(f"File too large: {len(file_content)} bytes (max: {self.max_file_size})")
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            raise TemplateServiceError(f"Invalid file type: {file_ext} (allowed: {self.allowed_extensions})")
        
        # Validate image content
        try:
            image = Image.open(BytesIO(file_content))
            image.verify()
        except Exception as e:
            raise TemplateServiceError(f"Invalid image file: {str(e)}")
    
    def _generate_template_id(self, user_id: str, filename: str) -> str:
        """Generate unique template ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(f"{user_id}_{filename}_{timestamp}".encode()).hexdigest()[:8]
        return f"tpl_{timestamp}_{content_hash}"
    
    async def _save_file(self, file_content: bytes, template_id: str, filename: str) -> Path:
        """Save uploaded file to disk"""
        file_ext = Path(filename).suffix.lower()
        file_path = self.upload_dir / f"{template_id}{file_ext}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return file_path
    
    async def _cache_template_data(self, template_id: str, template_data: Dict[str, Any]) -> None:
        """Cache template data in Redis"""
        cache_key = f"template:{template_id}"
        await redis_service.set(cache_key, template_data, self.cache_ttl)
    
    async def _get_cached_template_data(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template data from cache"""
        cache_key = f"template:{template_id}"
        return await redis_service.get(cache_key)
    
    async def _get_template_analysis(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template analysis results"""
        cache_key = f"template:analysis:{template_id}"
        return await redis_service.get(cache_key)
    
    async def _track_template_event(self, template_id: str, event: str, user_id: str) -> None:
        """Track template analytics event"""
        event_data = {
            "template_id": template_id,
            "event": event,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in Redis list (in production, use proper analytics DB)
        analytics_key = f"analytics:template:{template_id}"
        await redis_service.lpush(analytics_key, event_data)
        await redis_service.expire(analytics_key, 86400 * 30)  # 30 days
    
    async def _vector_search(
        self,
        query: Optional[str],
        embedding: Optional[List[float]],
        limit: int,
        threshold: float
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        if not query and not embedding:
            return []
        
        try:
            # Generate embedding if query provided
            if query and not embedding:
                embedding = await embedding_service.generate_embedding(query)
            
            # In production, this would query the database with pgvector
            # For now, simulate with cached embeddings
            results = []
            
            # Mock similarity search (replace with actual database query)
            template_ids = await self._get_all_template_ids()
            
            for template_id in template_ids[:limit]:
                cached_embedding = await redis_service.get(f"template:embedding:{template_id}")
                if cached_embedding:
                    # Calculate cosine similarity (simplified)
                    similarity = self._calculate_similarity(embedding, cached_embedding)
                    if similarity >= threshold:
                        results.append({
                            "template_id": template_id,
                            "similarity_score": similarity,
                            "search_type": "vector"
                        })
            
            # Sort by similarity
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            return results
            
        except Exception as e:
            logger.info(f"Vector search failed: {e}")
            return []
    
    async def _filter_search(
        self,
        category: Optional[str],
        tags: Optional[List[str]],
        user_id: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Perform filter-based search"""
        results = []
        
        # Mock filter search (replace with actual database query)
        template_ids = await self._get_all_template_ids()
        
        for template_id in template_ids[:limit]:
            template_data = await self._get_cached_template_data(template_id)
            if template_data and template_data.get("status") != "deleted":
                match = True
                
                if category and template_data.get("category") != category:
                    match = False
                
                if tags and not any(tag in template_data.get("tags", []) for tag in tags):
                    match = False
                
                if user_id and template_data.get("user_id") != user_id:
                    match = False
                
                if match:
                    results.append({
                        "template_id": template_id,
                        "similarity_score": 0.5,  # Default score for filter matches
                        "search_type": "filter"
                    })
        
        return results
    
    def _combine_search_results(
        self,
        vector_results: List[Dict[str, Any]],
        filter_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine and deduplicate search results"""
        combined = {}
        
        # Add vector results
        for result in vector_results:
            template_id = result["template_id"]
            combined[template_id] = result
        
        # Add filter results (don't override higher similarity scores)
        for result in filter_results:
            template_id = result["template_id"]
            if template_id not in combined:
                combined[template_id] = result
            else:
                # Keep higher similarity score
                if result["similarity_score"] > combined[template_id]["similarity_score"]:
                    combined[template_id] = result
        
        return list(combined.values())
    
    def _apply_search_filters(
        self,
        results: List[Dict[str, Any]],
        category: Optional[str],
        tags: Optional[List[str]],
        user_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Apply additional filters to search results"""
        # Sort by similarity score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results
    
    async def _enhance_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance search results with full template data"""
        enhanced = []
        
        for result in results:
            template_data = await self._get_cached_template_data(result["template_id"])
            if template_data:
                template_data["similarity_score"] = result["similarity_score"]
                template_data["search_type"] = result["search_type"]
                enhanced.append(template_data)
        
        return enhanced
    
    async def _get_popular_templates_from_analytics(
        self,
        start_time: datetime,
        category: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get popular templates from analytics data"""
        # Mock implementation (replace with actual analytics query)
        template_ids = await self._get_all_template_ids()
        
        popular = []
        for template_id in template_ids[:limit]:
            # Mock popularity metrics
            metrics = {
                "views": 100 + hash(template_id) % 500,
                "downloads": 20 + hash(template_id) % 100,
                "likes": 10 + hash(template_id) % 50
            }
            
            popular.append({
                "template_id": template_id,
                "metrics": metrics,
                "popularity_score": metrics["views"] + metrics["downloads"] * 2 + metrics["likes"] * 3
            })
        
        # Sort by popularity score
        popular.sort(key=lambda x: x["popularity_score"], reverse=True)
        return popular
    
    async def _get_all_template_ids(self) -> List[str]:
        """Get all template IDs (mock implementation)"""
        # In production, this would query the database
        # For now, return mock template IDs
        return [
            "tpl_20241007_120000_abc12345",
            "tpl_20241007_120001_def67890",
            "tpl_20241007_120002_ghi11111"
        ]
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            # Simple dot product similarity (replace with proper cosine similarity)
            if len(embedding1) != len(embedding2):
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            magnitude1 = sum(a * a for a in embedding1) ** 0.5
            magnitude2 = sum(b * b for b in embedding2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception:
            return 0.0

# Global template service instance
template_service = TemplateService()