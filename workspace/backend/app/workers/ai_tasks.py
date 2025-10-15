"""
AI-related Celery tasks
"""
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
from celery import current_task
from app.workers.celery_app import celery_app
from app.services.ai_service import vision_ai_service, AIServiceError
from app.services.embedding_service import embedding_service

@celery_app.task(bind=True, name="app.workers.ai_tasks.analyze_template_task")
def analyze_template_task(self, template_id: str, image_url: str) -> Dict[str, Any]:
    """
    Celery task for template analysis using AI vision
    """
    try:
        print(f"[{datetime.now(timezone.utc)}] Starting AI analysis for template {template_id}")
        
        # Update progress
        if current_task:
            current_task.update_state(
                state='PROGRESS',
                meta={'progress': 10, 'message': 'Initializing AI analysis...'}
            )
        
        # Run async analysis in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Analyze template
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 30, 'message': 'Analyzing image with AI vision...'}
                )
            
            analysis_result = loop.run_until_complete(
                vision_ai_service.analyze_template_image(image_url, template_id)
            )
            
            # Generate embedding
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 70, 'message': 'Generating embeddings...'}
                )
            
            searchable_text = analysis_result.get('searchable_text', '')
            if searchable_text:
                embedding = loop.run_until_complete(
                    embedding_service.generate_embedding(searchable_text)
                )
                analysis_result['embedding'] = embedding
            
            # Finalize
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={'progress': 100, 'message': 'Analysis complete'}
                )
            
            result = {
                'template_id': template_id,
                'status': 'completed',
                'analysis': analysis_result,
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
            print(f"[{datetime.now(timezone.utc)}] AI analysis completed for template {template_id}")
            return result
            
        finally:
            loop.close()
        
    except AIServiceError as e:
        error_msg = f"AI analysis failed for template {template_id}: {str(e)}"
        print(f"[{datetime.now(timezone.utc)}] {error_msg}")
        
        # Retry logic
        if self.request.retries < 2:
            raise self.retry(exc=e, countdown=60, max_retries=2)
        
        return {
            'template_id': template_id,
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        error_msg = f"Unexpected error in AI analysis for template {template_id}: {str(e)}"
        print(f"[{datetime.now(timezone.utc)}] {error_msg}")
        
        return {
            'template_id': template_id,
            'status': 'error',
            'error': str(e),
            'failed_at': datetime.now(timezone.utc).isoformat()
        }

@celery_app.task(name="app.workers.ai_tasks.generate_embedding_task")
def generate_embedding_task(text: str, cache_key: str = None) -> Dict[str, Any]:
    """
    Celery task for generating text embeddings
    """
    try:
        print(f"[{datetime.now(timezone.utc)}] Generating embedding for text (length: {len(text)})")
        
        # Run async embedding generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            embedding = loop.run_until_complete(
                embedding_service.generate_embedding(text)
            )
            
            result = {
                'status': 'completed',
                'embedding': embedding,
                'text_length': len(text),
                'cache_key': cache_key,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            print(f"[{datetime.now(timezone.utc)}] Embedding generation completed")
            return result
            
        finally:
            loop.close()
        
    except Exception as e:
        error_msg = f"Embedding generation failed: {str(e)}"
        print(f"[{datetime.now(timezone.utc)}] {error_msg}")
        
        return {
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now(timezone.utc).isoformat()
        }

@celery_app.task(bind=True, name="app.workers.ai_tasks.batch_analyze_templates_task")
def batch_analyze_templates_task(self, template_batch: list) -> Dict[str, Any]:
    """
    Celery task for batch template analysis
    """
    try:
        print(f"[{datetime.now(timezone.utc)}] Starting batch AI analysis for {len(template_batch)} templates")
        
        results = []
        total_templates = len(template_batch)
        
        for i, template_data in enumerate(template_batch):
            template_id = template_data['id']
            image_url = template_data['image_url']
            
            # Update progress
            progress = int((i / total_templates) * 100)
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'progress': progress,
                        'message': f'Analyzing template {i+1}/{total_templates}',
                        'current_template': template_id
                    }
                )
            
            # Analyze individual template
            try:
                result = analyze_template_task.apply_async(
                    args=[template_id, image_url]
                ).get(timeout=300)  # 5 minute timeout
                
                results.append({
                    'template_id': template_id,
                    'status': 'success',
                    'result': result
                })
                
            except Exception as e:
                print(f"[{datetime.now(timezone.utc)}] Failed to analyze template {template_id}: {str(e)}")
                results.append({
                    'template_id': template_id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        batch_result = {
            'batch_id': f"ai_batch_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            'total_templates': total_templates,
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'results': results,
            'completed_at': datetime.now(timezone.utc).isoformat()
        }
        
        print(f"[{datetime.now(timezone.utc)}] Batch AI analysis completed: {batch_result['successful']}/{total_templates} successful")
        return batch_result
        
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Batch AI analysis failed: {str(e)}")
        raise self.retry(exc=e, countdown=120, max_retries=2)