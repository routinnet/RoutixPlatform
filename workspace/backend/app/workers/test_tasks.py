"""
Test tasks for verifying Celery functionality
"""
import time
import asyncio
from datetime import datetime, timezone
from celery import current_task
from app.workers.celery_app import celery_app
from app.core.config import settings

@celery_app.task(bind=True, name="app.workers.test_tasks.test_basic_task")
def test_basic_task(self, message: str = "Hello from Celery!"):
    """
    Basic test task to verify Celery is working
    """
    try:
        print(f"[{datetime.now(timezone.utc)}] Executing test task: {message}")
        
        # Simulate some work
        for i in range(5):
            time.sleep(1)
            print(f"[{datetime.now(timezone.utc)}] Progress: {i+1}/5")
            
            # Update task progress
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={'current': i+1, 'total': 5, 'message': f'Processing step {i+1}'}
                )
        
        result = {
            'status': 'completed',
            'message': message,
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'task_id': self.request.id
        }
        
        print(f"[{datetime.now(timezone.utc)}] Task completed successfully")
        return result
        
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Task failed: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name="app.workers.test_tasks.test_async_task")
def test_async_task(self, data: dict):
    """
    Test task that simulates async operations
    """
    try:
        print(f"[{datetime.now(timezone.utc)}] Starting async test task with data: {data}")
        
        # Simulate async work
        steps = ['initialize', 'process', 'validate', 'finalize']
        
        for i, step in enumerate(steps):
            time.sleep(2)  # Simulate work
            
            progress = int((i + 1) / len(steps) * 100)
            
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': len(steps),
                        'step': step,
                        'progress': progress,
                        'message': f'Executing {step}...'
                    }
                )
            
            print(f"[{datetime.now(timezone.utc)}] Step {i+1}/{len(steps)}: {step} ({progress}%)")
        
        result = {
            'status': 'success',
            'input_data': data,
            'steps_completed': steps,
            'execution_time': len(steps) * 2,
            'completed_at': datetime.now(timezone.utc).isoformat()
        }
        
        return result
        
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Async task failed: {str(e)}")
        raise self.retry(exc=e, countdown=30, max_retries=2)

@celery_app.task(name="app.workers.test_tasks.health_check_task")
def health_check_task():
    """
    Health check task for monitoring
    """
    try:
        # Check Redis connection
        from redis import Redis
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_ping = redis_client.ping()
        
        # Check system resources
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        health_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'redis_connected': redis_ping,
            'cpu_usage': cpu_percent,
            'memory_usage': memory_percent,
            'celery_worker': 'healthy'
        }
        
        print(f"[{datetime.now(timezone.utc)}] Health check completed: {health_data}")
        return health_data
        
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Health check failed: {str(e)}")
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'unhealthy',
            'error': str(e)
        }

@celery_app.task(bind=True, name="app.workers.test_tasks.test_error_handling")
def test_error_handling(self, should_fail: bool = False):
    """
    Test task for error handling and retry logic
    """
    try:
        print(f"[{datetime.now(timezone.utc)}] Testing error handling (should_fail={should_fail})")
        
        if should_fail:
            raise ValueError("Intentional test error")
        
        return {
            'status': 'success',
            'message': 'Error handling test passed',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Task error (attempt {self.request.retries + 1}): {str(e)}")
        
        if self.request.retries < 2:  # Retry up to 2 times
            raise self.retry(exc=e, countdown=10, max_retries=2)
        else:
            return {
                'status': 'failed',
                'error': str(e),
                'retries': self.request.retries,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }