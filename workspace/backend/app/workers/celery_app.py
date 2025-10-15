"""
Celery Application Configuration for Routix Platform
Task routing, performance tuning, and beat scheduling
"""
from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    'routix',
    broker=settings.REDIS_URL or 'redis://localhost:6379/0',
    backend=settings.REDIS_URL or 'redis://localhost:6379/0'
)

# Task routing configuration for 3 specialized queues
celery_app.conf.task_routes = {
    # Template Analysis Queue
    'app.workers.template_analysis.analyze_template_task': {'queue': 'analysis'},
    'app.workers.template_analysis.batch_analyze_templates_task': {'queue': 'analysis'},
    'app.workers.template_analysis.monitor_batch_analysis_task': {'queue': 'analysis'},
    
    # Generation Pipeline Queue
    'app.workers.generation_pipeline.generate_thumbnail_task': {'queue': 'generation'},
    'app.workers.generation_pipeline.batch_generate_thumbnails_task': {'queue': 'generation'},
    
    # Maintenance and Cleanup Queue
    'app.workers.cleanup_tasks.cleanup_old_generations': {'queue': 'maintenance'},
    'app.workers.cleanup_tasks.cleanup_expired_tokens': {'queue': 'maintenance'},
    'app.workers.cleanup_tasks.aggregate_daily_analytics': {'queue': 'maintenance'},
    'app.workers.cleanup_tasks.system_health_check': {'queue': 'maintenance'},
}

# Queue definitions with priority and routing
celery_app.conf.task_queue_max_priority = 10
celery_app.conf.task_default_priority = 5

# Define queues with different priorities
celery_app.conf.task_queues = (
    # High-priority generation queue
    Queue('generation', 
          Exchange('generation'), 
          routing_key='generation',
          queue_arguments={'x-max-priority': 10}),
    
    # Medium-priority analysis queue
    Queue('analysis', 
          Exchange('analysis'), 
          routing_key='analysis',
          queue_arguments={'x-max-priority': 7}),
    
    # Low-priority maintenance queue
    Queue('maintenance', 
          Exchange('maintenance'), 
          routing_key='maintenance',
          queue_arguments={'x-max-priority': 3}),
)

# Performance tuning configuration
celery_app.conf.update(
    # Serialization settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minutes soft limit
    task_acks_late=True,  # Acknowledge after task completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker dies
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # One task at a time for better resource management
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (memory management)
    worker_disable_rate_limits=False,  # Enable rate limiting
    worker_pool_restarts=True,  # Allow pool restarts
    
    # Result backend configuration
    result_expires=3600,  # Keep results for 1 hour
    result_extended=True,  # Store additional metadata
    result_compression='gzip',  # Compress results
    result_chord_join_timeout=300,  # 5 minutes for chord joins
    
    # Connection settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Task retry configuration
    task_default_retry_delay=60,  # 1 minute default retry delay
    task_max_retries=3,  # Maximum retries for tasks
    
    # Monitoring and logging
    worker_send_task_events=True,  # Send task events for monitoring
    task_send_sent_event=True,  # Send task sent events
    
    # Memory and resource management
    worker_max_memory_per_child=200000,  # 200MB per worker child (KB)
    worker_purge_offline_workers=True,  # Remove offline workers
    
    # Security settings
    worker_hijack_root_logger=False,  # Don't hijack root logger
    worker_log_color=True,  # Colored logs for better readability
    
    # Beat scheduler settings
    beat_schedule_filename='celerybeat-schedule',  # Schedule file location
    beat_sync_every=1,  # Sync schedule every task
    beat_max_loop_interval=300,  # Maximum beat loop interval (5 minutes)
)

# Celery Beat schedule configuration for maintenance tasks
celery_app.conf.beat_schedule = {
    # Daily cleanup of old generations at 3 AM
    'cleanup-old-generations': {
        'task': 'app.workers.cleanup_tasks.cleanup_old_generations',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3:00 AM
        'options': {'queue': 'maintenance', 'priority': 2}
    },
    
    # Hourly cleanup of expired tokens
    'cleanup-expired-tokens': {
        'task': 'app.workers.cleanup_tasks.cleanup_expired_tokens',
        'schedule': crontab(minute=0),  # Every hour at minute 0
        'options': {'queue': 'maintenance', 'priority': 3}
    },
    
    # Daily analytics aggregation at 1 AM
    'aggregate-daily-analytics': {
        'task': 'app.workers.cleanup_tasks.aggregate_daily_analytics',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1:00 AM
        'options': {'queue': 'maintenance', 'priority': 4}
    },
    
    # System health check every 6 hours
    'system-health-check': {
        'task': 'app.workers.cleanup_tasks.system_health_check',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'options': {'queue': 'maintenance', 'priority': 5}
    },
    
    # Weekly deep cleanup on Sundays at 2 AM
    'weekly-deep-cleanup': {
        'task': 'app.workers.cleanup_tasks.cleanup_old_generations',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday at 2:00 AM
        'options': {'queue': 'maintenance', 'priority': 1}
    },
    
    # Monthly analytics report on 1st day at midnight
    'monthly-analytics-report': {
        'task': 'app.workers.cleanup_tasks.aggregate_daily_analytics',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),  # 1st of month at midnight
        'options': {'queue': 'maintenance', 'priority': 6}
    }
}

# Advanced worker configuration for different queue types
WORKER_CONFIGURATIONS = {
    'generation': {
        'concurrency': 2,  # Limit concurrent generation tasks
        'max_memory_per_child': 300000,  # 300MB for generation workers
        'time_limit': 1800,  # 30 minutes for generation tasks
        'soft_time_limit': 1500,  # 25 minutes soft limit
    },
    
    'analysis': {
        'concurrency': 4,  # More concurrent analysis tasks
        'max_memory_per_child': 200000,  # 200MB for analysis workers
        'time_limit': 900,  # 15 minutes for analysis tasks
        'soft_time_limit': 720,  # 12 minutes soft limit
    },
    
    'maintenance': {
        'concurrency': 1,  # Single maintenance worker
        'max_memory_per_child': 150000,  # 150MB for maintenance workers
        'time_limit': 3600,  # 1 hour for maintenance tasks
        'soft_time_limit': 3300,  # 55 minutes soft limit
    }
}

# Error handling and retry configuration
RETRY_KWARGS = {
    'max_retries': 3,
    'countdown': 60,  # 1 minute base countdown
    'backoff': True,  # Exponential backoff
    'jitter': True,  # Add jitter to prevent thundering herd
}

# Task priority mapping
TASK_PRIORITIES = {
    # High priority (8-10)
    'generate_thumbnail_task': 9,
    'batch_generate_thumbnails_task': 8,
    
    # Medium priority (5-7)
    'analyze_template_task': 6,
    'batch_analyze_templates_task': 5,
    
    # Low priority (1-4)
    'cleanup_old_generations': 2,
    'cleanup_expired_tokens': 3,
    'aggregate_daily_analytics': 4,
    'system_health_check': 4,
}

# Monitoring and health check configuration
MONITORING_CONFIG = {
    'health_check_interval': 300,  # 5 minutes
    'worker_heartbeat_interval': 30,  # 30 seconds
    'task_timeout_threshold': 1800,  # 30 minutes
    'memory_threshold': 250000,  # 250MB memory threshold
    'queue_length_threshold': 100,  # Alert if queue length > 100
}

# Development vs Production configuration
if settings.ENVIRONMENT == 'development':
    # Development-specific settings
    celery_app.conf.update(
        task_always_eager=False,  # Don't execute tasks synchronously
        task_eager_propagates=True,  # Propagate exceptions in eager mode
        worker_log_level='DEBUG',  # Debug logging
        worker_concurrency=2,  # Lower concurrency for development
    )
else:
    # Production-specific settings
    celery_app.conf.update(
        task_always_eager=False,
        worker_log_level='INFO',  # Info logging
        worker_concurrency=4,  # Higher concurrency for production
        broker_pool_limit=10,  # Connection pool limit
        result_backend_max_retries=3,  # Result backend retries
    )

# Custom task base class for enhanced functionality
class BaseTask(celery_app.Task):
    """Base task class with enhanced error handling and logging"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(f'Task {task_id} failed: {exc}')
        # In production: send alerts, log to monitoring system
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        logger.info(f'Task {task_id} succeeded')
        # In production: update metrics, log success
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry"""
        logger.warning(f'Task {task_id} retrying: {exc}')
        # In production: log retry attempts

# Set custom base task
celery_app.Task = BaseTask

# Signal handlers for monitoring
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration"""
    logger.debug(f'Request: {self.request!r}')
    return 'Debug task completed successfully'

# Worker startup configuration
def configure_worker_for_queue(queue_name: str):
    """Configure worker settings based on queue type"""
    config = WORKER_CONFIGURATIONS.get(queue_name, {})
    
    for setting, value in config.items():
        setattr(celery_app.conf, f'worker_{setting}', value)

# Export Celery app and configuration
__all__ = [
    'celery_app', 
    'WORKER_CONFIGURATIONS', 
    'TASK_PRIORITIES', 
    'MONITORING_CONFIG',
    'configure_worker_for_queue'
]
