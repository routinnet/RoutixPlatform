"""
Celery application configuration for Routix Platform
"""
import os
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "routix",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.workers.template_analysis',
        'app.workers.generation_pipeline', 
        'app.workers.cleanup_tasks',
        'app.workers.test_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },
    
    # Task routing
    task_routes={
        'app.workers.template_analysis.*': {'queue': 'template_analysis'},
        'app.workers.generation_pipeline.*': {'queue': 'generation'},
        'app.workers.cleanup_tasks.*': {'queue': 'cleanup'},
        'app.workers.test_tasks.*': {'queue': 'test'},
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Beat scheduler settings
    beat_schedule={
        'cleanup-expired-generations': {
            'task': 'app.workers.cleanup_tasks.cleanup_expired_generations',
            'schedule': 3600.0,  # Every hour
        },
        'update-template-performance': {
            'task': 'app.workers.cleanup_tasks.update_template_performance_metrics',
            'schedule': 1800.0,  # Every 30 minutes
        },
        'health-check': {
            'task': 'app.workers.test_tasks.health_check_task',
            'schedule': 300.0,  # Every 5 minutes
        },
    },
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Error handling
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
)

# Optional configuration based on environment
if settings.ENVIRONMENT == "development":
    celery_app.conf.update(
        task_always_eager=False,  # Set to True for synchronous testing
        task_eager_propagates=True,
        worker_log_level='DEBUG',
    )
elif settings.ENVIRONMENT == "production":
    celery_app.conf.update(
        worker_log_level='INFO',
        task_compression='gzip',
        result_compression='gzip',
    )

# Auto-discover tasks
celery_app.autodiscover_tasks()

if __name__ == '__main__':
    celery_app.start()