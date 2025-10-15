"""
Enhanced generation pipeline tasks with Midjourney integration
"""
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from celery import current_task
from app.workers.celery_app import celery_app
from app.services.midjourney_service import midjourney_service, MidjourneyServiceError
from app.services.ai_service import vision_ai_service, embedding_service
from app.services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.workers.generation_tasks.generate_thumbnail_with_midjourney")
def generate_thumbnail_with_midjourney(
    self,
    generation_request: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate thumbnail using Midjourney with template analysis
    """
    try:
        request_id = generation_request['id']
        user_id = generation_request['user_id']
        prompt = generation_request['prompt']
        template_id = generation_request.get('template_id')
        user_face_url = generation_request.get('user_face_url')
        user_logo_url = generation_request.get('user_logo_url')
        custom_text = generation_request.get('custom_text')
        
        logger.info(f"Starting Midjourney generation for request {request_id}")
        
        # Update progress
        if current_task:
            current_task.update_state(
                state='PROGRESS',
                meta={'progress': 10, 'message': 'Initializing generation...', 'status': 'analyzing'}
            )
        
        # Run async generation in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Step 1: Get template analysis if template_id provided
            template_analysis = None
            if template_id:
                if current_task:
                    current_task.update_state(
                        state='PROGRESS',
                        meta={'progress': 20, 'message': 'Analyzing template...', 'status': 'analyzing'}
                    )
                
                # Get cached template analysis or analyze new template
                cache_key = f"template:analysis:{template_id}"
                template_analysis = loop.run_until_complete(
                    redis_service.get(cache_key)
                )
                
                if not template_analysis:
                    logger.info(f"Template analysis not found for {template_id}, skipping style reference")
            
            # Step 2: Generate with Midjourney
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 30, 'message': 'Submitting to Midjourney...', 'status': 'generating'}
                )
            
            generation_result = loop.run_until_complete(
                midjourney_service.generate_thumbnail(
                    prompt=prompt,
                    template_analysis=template_analysis,
                    user_face_url=user_face_url,
                    user_logo_url=user_logo_url,
                    custom_text=custom_text,
                    aspect_ratio="16:9",
                    model="v6"
                )
            )
            
            # Step 3: Process result
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 90, 'message': 'Processing result...', 'status': 'processing'}
                )
            
            # Finalize result
            final_result = {
                'request_id': request_id,
                'user_id': user_id,
                'status': 'completed',
                'image_url': generation_result['image_url'],
                'generation_metadata': {
                    'prompt_used': generation_result['metadata']['prompt_used'],
                    'midjourney_service': generation_result['metadata']['midjourney_service'],
                    'generation_time': generation_result.get('generation_time', 0),
                    'quality_score': generation_result['metadata'].get('quality_score', 0.8),
                    'template_analysis_used': generation_result['metadata'].get('template_analysis_used', False)
                },
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 100, 'message': 'Generation complete', 'status': 'completed'}
                )
            
            logger.info(f"Midjourney generation completed for request {request_id}")
            return final_result
            
        finally:
            loop.close()
        
    except MidjourneyServiceError as e:
        error_msg = f"Midjourney generation failed for request {request_id}: {str(e)}"
        logger.error(error_msg)
        
        # Retry logic for certain errors
        if "timeout" in str(e).lower() or "queue" in str(e).lower():
            if self.request.retries < 2:
                raise self.retry(exc=e, countdown=120, max_retries=2)
        
        return {
            'request_id': request_id,
            'status': 'failed',
            'error': str(e),
            'error_type': 'midjourney_service_error',
            'failed_at': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        error_msg = f"Unexpected error in Midjourney generation for request {request_id}: {str(e)}"
        logger.error(error_msg)
        
        return {
            'request_id': request_id,
            'status': 'error',
            'error': str(e),
            'error_type': 'system_error',
            'failed_at': datetime.now(timezone.utc).isoformat()
        }

@celery_app.task(bind=True, name="app.workers.generation_tasks.upscale_thumbnail")
def upscale_thumbnail(
    self,
    task_id: str,
    service: str,
    upscale_index: int = 1
) -> Dict[str, Any]:
    """
    Upscale a generated thumbnail
    """
    try:
        logger.info(f"Starting thumbnail upscale for task {task_id}")
        
        # Update progress
        if current_task:
            current_task.update_state(
                state='PROGRESS',
                meta={'progress': 20, 'message': 'Submitting upscale request...'}
            )
        
        # Run async upscale in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            upscale_result = loop.run_until_complete(
                midjourney_service.upscale_image(task_id, upscale_index, service)
            )
            
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 100, 'message': 'Upscale complete'}
                )
            
            result = {
                'original_task_id': task_id,
                'upscale_index': upscale_index,
                'status': 'completed',
                'upscaled_image_url': upscale_result['image_url'],
                'upscale_metadata': {
                    'service': service,
                    'generation_time': upscale_result.get('generation_time', 0),
                    'quality_score': upscale_result.get('metadata', {}).get('quality_score', 0.9)
                },
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Thumbnail upscale completed for task {task_id}")
            return result
            
        finally:
            loop.close()
        
    except MidjourneyServiceError as e:
        error_msg = f"Thumbnail upscale failed for task {task_id}: {str(e)}"
        logger.error(error_msg)
        
        return {
            'original_task_id': task_id,
            'upscale_index': upscale_index,
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        error_msg = f"Unexpected error in thumbnail upscale for task {task_id}: {str(e)}"
        logger.error(error_msg)
        
        return {
            'original_task_id': task_id,
            'upscale_index': upscale_index,
            'status': 'error',
            'error': str(e),
            'failed_at': datetime.now(timezone.utc).isoformat()
        }

@celery_app.task(bind=True, name="app.workers.generation_tasks.batch_generate_thumbnails")
def batch_generate_thumbnails(
    self,
    generation_requests: list
) -> Dict[str, Any]:
    """
    Generate multiple thumbnails in batch
    """
    try:
        logger.info(f"Starting batch Midjourney generation for {len(generation_requests)} requests")
        
        results = []
        total_requests = len(generation_requests)
        
        for i, request_data in enumerate(generation_requests):
            request_id = request_data['id']
            
            # Update overall progress
            progress = int((i / total_requests) * 100)
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'progress': progress,
                        'message': f'Processing request {i+1}/{total_requests}',
                        'current_request': request_id
                    }
                )
            
            try:
                # Generate individual thumbnail
                result = generate_thumbnail_with_midjourney.apply_async(
                    args=[request_data]
                ).get(timeout=900)  # 15 minute timeout
                
                results.append({
                    'request_id': request_id,
                    'status': 'success',
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Failed to generate thumbnail for request {request_id}: {str(e)}")
                results.append({
                    'request_id': request_id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        batch_result = {
            'batch_id': f"mj_batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            'total_requests': total_requests,
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'results': results,
            'completed_at': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Batch Midjourney generation completed: {batch_result['successful']}/{total_requests} successful")
        return batch_result
        
    except Exception as e:
        logger.error(f"Batch Midjourney generation failed: {str(e)}")
        raise self.retry(exc=e, countdown=180, max_retries=2)
