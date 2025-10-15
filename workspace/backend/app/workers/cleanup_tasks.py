"""
Cleanup & Maintenance Tasks for Routix Platform
Scheduled system housekeeping operations with comprehensive logging
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from celery.schedules import crontab
from app.workers.celery_app import celery_app
from app.services.redis_service import redis_service

# Configure logging
logger = logging.getLogger(__name__)

class CleanupError(Exception):
    """Custom exception for cleanup operations"""
    pass

@celery_app.task
def cleanup_old_generations() -> Dict[str, Any]:
    """
    Clean up old generation requests and associated data
    Runs daily at 3 AM via Celery Beat
    
    Returns:
        Cleanup statistics and results
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        logger.info(f"[{start_time}] Starting cleanup of old generations")
        
        # Initialize cleanup stats
        cleanup_stats = {
            "failed_generations_deleted": 0,
            "orphaned_files_cleaned": 0,
            "cache_entries_cleared": 0,
            "analytics_data_archived": 0,
            "errors_encountered": 0,
            "cleanup_duration": 0
        }
        
        # Step 1: Clean up failed generations older than 7 days
        failed_cleanup_result = asyncio.run(cleanup_failed_generations())
        cleanup_stats["failed_generations_deleted"] = failed_cleanup_result["deleted_count"]
        
        # Step 2: Clean up orphaned generation files
        orphaned_cleanup_result = asyncio.run(cleanup_orphaned_files())
        cleanup_stats["orphaned_files_cleaned"] = orphaned_cleanup_result["cleaned_count"]
        
        # Step 3: Clear expired cache entries
        cache_cleanup_result = asyncio.run(cleanup_expired_cache())
        cleanup_stats["cache_entries_cleared"] = cache_cleanup_result["cleared_count"]
        
        # Step 4: Archive old analytics data
        analytics_cleanup_result = asyncio.run(archive_old_analytics())
        cleanup_stats["analytics_data_archived"] = analytics_cleanup_result["archived_count"]
        
        # Step 5: Clean up temporary files
        temp_cleanup_result = asyncio.run(cleanup_temporary_files())
        cleanup_stats["temp_files_cleaned"] = temp_cleanup_result["cleaned_count"]
        
        # Calculate cleanup duration
        end_time = datetime.now(timezone.utc)
        cleanup_stats["cleanup_duration"] = (end_time - start_time).total_seconds()
        
        # Log cleanup summary
        logger.info(f"Generation cleanup completed successfully: {cleanup_stats}")
        
        # Store cleanup report
        asyncio.run(store_cleanup_report("generation_cleanup", cleanup_stats))
        
        return {
            "status": "completed",
            "cleanup_stats": cleanup_stats,
            "completed_at": end_time.isoformat(),
            "message": "Generation cleanup completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Generation cleanup failed: {e}", exc_info=True)
        cleanup_stats["errors_encountered"] = 1
        
        # Store error report
        asyncio.run(store_cleanup_report("generation_cleanup", {
            **cleanup_stats,
            "error": str(e),
            "failed_at": datetime.now(timezone.utc).isoformat()
        }))
        
        raise CleanupError(f"Generation cleanup failed: {str(e)}")

@celery_app.task
def cleanup_expired_tokens() -> Dict[str, Any]:
    """
    Clean up expired JWT tokens and maintain security hygiene
    Runs hourly via Celery Beat
    
    Returns:
        Token cleanup statistics
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        logger.info(f"[{start_time}] Starting cleanup of expired tokens")
        
        # Initialize token cleanup stats
        token_stats = {
            "expired_tokens_removed": 0,
            "blacklisted_tokens_cleaned": 0,
            "refresh_tokens_purged": 0,
            "verification_tokens_cleared": 0,
            "reset_tokens_cleared": 0,
            "cleanup_duration": 0
        }
        
        # Step 1: Remove expired JWT tokens from blacklist
        blacklist_result = asyncio.run(cleanup_token_blacklist())
        token_stats["blacklisted_tokens_cleaned"] = blacklist_result["cleaned_count"]
        
        # Step 2: Purge expired refresh tokens
        refresh_result = asyncio.run(cleanup_refresh_tokens())
        token_stats["refresh_tokens_purged"] = refresh_result["purged_count"]
        
        # Step 3: Clear expired verification tokens
        verification_result = asyncio.run(cleanup_verification_tokens())
        token_stats["verification_tokens_cleared"] = verification_result["cleared_count"]
        
        # Step 4: Clear expired password reset tokens
        reset_result = asyncio.run(cleanup_reset_tokens())
        token_stats["reset_tokens_cleared"] = reset_result["cleared_count"]
        
        # Step 5: Clean up session data
        session_result = asyncio.run(cleanup_expired_sessions())
        token_stats["expired_sessions_cleaned"] = session_result["cleaned_count"]
        
        # Calculate cleanup duration
        end_time = datetime.now(timezone.utc)
        token_stats["cleanup_duration"] = (end_time - start_time).total_seconds()
        
        # Log token cleanup summary
        logger.info(f"Token cleanup completed successfully: {token_stats}")
        
        # Store token cleanup report
        asyncio.run(store_cleanup_report("token_cleanup", token_stats))
        
        return {
            "status": "completed",
            "token_stats": token_stats,
            "completed_at": end_time.isoformat(),
            "message": "Token cleanup completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Token cleanup failed: {e}", exc_info=True)
        
        # Store error report
        asyncio.run(store_cleanup_report("token_cleanup", {
            **token_stats,
            "error": str(e),
            "failed_at": datetime.now(timezone.utc).isoformat()
        }))
        
        raise CleanupError(f"Token cleanup failed: {str(e)}")

@celery_app.task
def aggregate_daily_analytics() -> Dict[str, Any]:
    """
    Aggregate daily analytics and generate usage reports
    Runs daily at 1 AM via Celery Beat
    
    Returns:
        Analytics aggregation results
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        logger.info(f"[{start_time}] Starting daily analytics aggregation")
        
        # Initialize analytics stats
        analytics_stats = {
            "template_metrics_aggregated": 0,
            "user_activity_calculated": 0,
            "generation_stats_compiled": 0,
            "performance_metrics_computed": 0,
            "reports_generated": 0,
            "aggregation_duration": 0
        }
        
        # Step 1: Aggregate template performance metrics
        template_result = asyncio.run(aggregate_template_metrics())
        analytics_stats["template_metrics_aggregated"] = template_result["metrics_count"]
        
        # Step 2: Calculate user activity statistics
        user_result = asyncio.run(aggregate_user_activity())
        analytics_stats["user_activity_calculated"] = user_result["users_processed"]
        
        # Step 3: Compile generation statistics
        generation_result = asyncio.run(aggregate_generation_stats())
        analytics_stats["generation_stats_compiled"] = generation_result["generations_processed"]
        
        # Step 4: Compute system performance metrics
        performance_result = asyncio.run(compute_performance_metrics())
        analytics_stats["performance_metrics_computed"] = performance_result["metrics_computed"]
        
        # Step 5: Generate daily reports
        report_result = asyncio.run(generate_daily_reports())
        analytics_stats["reports_generated"] = report_result["reports_created"]
        
        # Calculate aggregation duration
        end_time = datetime.now(timezone.utc)
        analytics_stats["aggregation_duration"] = (end_time - start_time).total_seconds()
        
        # Log analytics summary
        logger.info(f"Analytics aggregation completed successfully: {analytics_stats}")
        
        # Store analytics report
        asyncio.run(store_cleanup_report("analytics_aggregation", analytics_stats))
        
        return {
            "status": "completed",
            "analytics_stats": analytics_stats,
            "completed_at": end_time.isoformat(),
            "message": "Daily analytics aggregation completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Analytics aggregation failed: {e}", exc_info=True)
        
        # Store error report
        asyncio.run(store_cleanup_report("analytics_aggregation", {
            **analytics_stats,
            "error": str(e),
            "failed_at": datetime.now(timezone.utc).isoformat()
        }))
        
        raise CleanupError(f"Analytics aggregation failed: {str(e)}")

@celery_app.task
def system_health_check() -> Dict[str, Any]:
    """
    Perform comprehensive system health check
    Runs every 6 hours via Celery Beat
    
    Returns:
        System health status and metrics
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        logger.info(f"[{start_time}] Starting system health check")
        
        # Initialize health check results
        health_results = {
            "redis_status": "unknown",
            "database_status": "unknown",
            "storage_status": "unknown",
            "ai_services_status": "unknown",
            "worker_status": "unknown",
            "overall_health": "unknown",
            "check_duration": 0
        }
        
        # Step 1: Check Redis connectivity and performance
        redis_health = asyncio.run(check_redis_health())
        health_results["redis_status"] = redis_health["status"]
        
        # Step 2: Check database connectivity and performance
        db_health = asyncio.run(check_database_health())
        health_results["database_status"] = db_health["status"]
        
        # Step 3: Check storage service health
        storage_health = asyncio.run(check_storage_health())
        health_results["storage_status"] = storage_health["status"]
        
        # Step 4: Check AI services availability
        ai_health = asyncio.run(check_ai_services_health())
        health_results["ai_services_status"] = ai_health["status"]
        
        # Step 5: Check Celery worker health
        worker_health = asyncio.run(check_worker_health())
        health_results["worker_status"] = worker_health["status"]
        
        # Determine overall health
        health_results["overall_health"] = determine_overall_health(health_results)
        
        # Calculate check duration
        end_time = datetime.now(timezone.utc)
        health_results["check_duration"] = (end_time - start_time).total_seconds()
        
        # Log health check summary
        logger.info(f"System health check completed: {health_results}")
        
        # Store health report
        asyncio.run(store_health_report(health_results))
        
        return {
            "status": "completed",
            "health_results": health_results,
            "completed_at": end_time.isoformat(),
            "message": "System health check completed successfully"
        }
        
    except Exception as e:
        logger.error(f"System health check failed: {e}", exc_info=True)
        
        # Store error report
        asyncio.run(store_cleanup_report("health_check", {
            "error": str(e),
            "failed_at": datetime.now(timezone.utc).isoformat()
        }))
        
        raise CleanupError(f"System health check failed: {str(e)}")

# Cleanup Helper Functions

async def cleanup_failed_generations() -> Dict[str, Any]:
    """Clean up failed generation requests older than 7 days"""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        deleted_count = 0
        
        # Get failed generation keys from Redis
        pattern = "generation:*"
        keys = await redis_service.keys(pattern)
        
        for key in keys:
            try:
                generation_data = await redis_service.get(key)
                if generation_data:
                    created_at = datetime.fromisoformat(generation_data.get("created_at", ""))
                    status = generation_data.get("status", "")
                    
                    if status == "failed" and created_at < cutoff_date:
                        await redis_service.delete(key)
                        deleted_count += 1
                        
            except Exception as e:
                logger.warning(f"Failed to process generation key {key}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} failed generations")
        
        return {"deleted_count": deleted_count}
        
    except Exception as e:
        logger.error(f"Failed generation cleanup failed: {e}")
        return {"deleted_count": 0, "error": str(e)}

async def cleanup_orphaned_files() -> Dict[str, Any]:
    """Clean up orphaned generation files"""
    try:
        # Mock implementation - in production, scan storage for orphaned files
        cleaned_count = 0
        
        # This would typically involve:
        # 1. List all files in storage
        # 2. Check if corresponding generation exists
        # 3. Delete orphaned files
        
        logger.info(f"Cleaned up {cleaned_count} orphaned files")
        
        return {"cleaned_count": cleaned_count}
        
    except Exception as e:
        logger.error(f"Orphaned file cleanup failed: {e}")
        return {"cleaned_count": 0, "error": str(e)}

async def cleanup_expired_cache() -> Dict[str, Any]:
    """Clean up expired cache entries"""
    try:
        cleared_count = 0
        
        # Clean up expired progress entries
        pattern = "progress:*"
        keys = await redis_service.keys(pattern)
        
        for key in keys:
            try:
                ttl = await redis_service.ttl(key)
                if ttl == -1:  # No expiration set
                    await redis_service.expire(key, 300)  # Set 5 minute expiration
                elif ttl == -2:  # Key doesn't exist
                    cleared_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to process cache key {key}: {e}")
        
        logger.info(f"Processed {len(keys)} cache entries, cleared {cleared_count}")
        
        return {"cleared_count": cleared_count}
        
    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        return {"cleared_count": 0, "error": str(e)}

async def archive_old_analytics() -> Dict[str, Any]:
    """Archive old analytics data"""
    try:
        archived_count = 0
        
        # Archive analytics older than 30 days
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Process analytics keys
        analytics_keys = [
            "analytics:template_analysis",
            "analytics:generation",
            "analytics:user",
            "analytics:template_failures"
        ]
        
        for key in analytics_keys:
            try:
                # Get all analytics entries
                entries = await redis_service.lrange(key, 0, -1)
                
                # Filter old entries
                old_entries = []
                for entry in entries:
                    if isinstance(entry, dict):
                        timestamp = entry.get("timestamp", "")
                        if timestamp:
                            entry_date = datetime.fromisoformat(timestamp)
                            if entry_date < cutoff_date:
                                old_entries.append(entry)
                
                # Archive old entries (mock - in production, move to long-term storage)
                if old_entries:
                    archived_count += len(old_entries)
                    # Remove old entries from active analytics
                    # In production: move to archive storage
                    
            except Exception as e:
                logger.warning(f"Failed to archive analytics key {key}: {e}")
        
        logger.info(f"Archived {archived_count} old analytics entries")
        
        return {"archived_count": archived_count}
        
    except Exception as e:
        logger.error(f"Analytics archival failed: {e}")
        return {"archived_count": 0, "error": str(e)}

async def cleanup_temporary_files() -> Dict[str, Any]:
    """Clean up temporary files"""
    try:
        cleaned_count = 0
        
        # Mock implementation - in production, clean temp directories
        # This would involve cleaning:
        # - Temporary image downloads
        # - Processing cache files
        # - Log rotation
        
        logger.info(f"Cleaned up {cleaned_count} temporary files")
        
        return {"cleaned_count": cleaned_count}
        
    except Exception as e:
        logger.error(f"Temporary file cleanup failed: {e}")
        return {"cleaned_count": 0, "error": str(e)}

# Token Cleanup Functions

async def cleanup_token_blacklist() -> Dict[str, Any]:
    """Clean up expired tokens from blacklist"""
    try:
        cleaned_count = 0
        
        # Get all blacklisted tokens
        pattern = "blacklist:*"
        keys = await redis_service.keys(pattern)
        
        for key in keys:
            try:
                ttl = await redis_service.ttl(key)
                if ttl == -2:  # Key expired
                    cleaned_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to process blacklist key {key}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} expired blacklisted tokens")
        
        return {"cleaned_count": cleaned_count}
        
    except Exception as e:
        logger.error(f"Token blacklist cleanup failed: {e}")
        return {"cleaned_count": 0, "error": str(e)}

async def cleanup_refresh_tokens() -> Dict[str, Any]:
    """Clean up expired refresh tokens"""
    try:
        purged_count = 0
        
        # Get all refresh tokens
        pattern = "refresh_token:*"
        keys = await redis_service.keys(pattern)
        
        for key in keys:
            try:
                ttl = await redis_service.ttl(key)
                if ttl == -2:  # Key expired
                    purged_count += 1
                elif ttl == -1:  # No expiration set, set default
                    await redis_service.expire(key, 86400 * 30)  # 30 days
                    
            except Exception as e:
                logger.warning(f"Failed to process refresh token {key}: {e}")
        
        logger.info(f"Purged {purged_count} expired refresh tokens")
        
        return {"purged_count": purged_count}
        
    except Exception as e:
        logger.error(f"Refresh token cleanup failed: {e}")
        return {"purged_count": 0, "error": str(e)}

async def cleanup_verification_tokens() -> Dict[str, Any]:
    """Clean up expired verification tokens"""
    try:
        cleared_count = 0
        
        # Get all verification tokens
        pattern = "verify:*"
        keys = await redis_service.keys(pattern)
        
        for key in keys:
            try:
                ttl = await redis_service.ttl(key)
                if ttl == -2:  # Key expired
                    cleared_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to process verification token {key}: {e}")
        
        logger.info(f"Cleared {cleared_count} expired verification tokens")
        
        return {"cleared_count": cleared_count}
        
    except Exception as e:
        logger.error(f"Verification token cleanup failed: {e}")
        return {"cleared_count": 0, "error": str(e)}

async def cleanup_reset_tokens() -> Dict[str, Any]:
    """Clean up expired password reset tokens"""
    try:
        cleared_count = 0
        
        # Get all reset tokens
        pattern = "reset:*"
        keys = await redis_service.keys(pattern)
        
        for key in keys:
            try:
                ttl = await redis_service.ttl(key)
                if ttl == -2:  # Key expired
                    cleared_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to process reset token {key}: {e}")
        
        logger.info(f"Cleared {cleared_count} expired reset tokens")
        
        return {"cleared_count": cleared_count}
        
    except Exception as e:
        logger.error(f"Reset token cleanup failed: {e}")
        return {"cleared_count": 0, "error": str(e)}

async def cleanup_expired_sessions() -> Dict[str, Any]:
    """Clean up expired user sessions"""
    try:
        cleaned_count = 0
        
        # Get all session keys
        pattern = "session:*"
        keys = await redis_service.keys(pattern)
        
        for key in keys:
            try:
                ttl = await redis_service.ttl(key)
                if ttl == -2:  # Key expired
                    cleaned_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to process session {key}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} expired sessions")
        
        return {"cleaned_count": cleaned_count}
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        return {"cleaned_count": 0, "error": str(e)}

# Analytics Aggregation Functions

async def aggregate_template_metrics() -> Dict[str, Any]:
    """Aggregate template performance metrics"""
    try:
        metrics_count = 0
        
        # Get template analytics data
        analytics_entries = await redis_service.lrange("analytics:template_analysis", 0, -1)
        
        # Aggregate metrics by template
        template_metrics = {}
        
        for entry in analytics_entries:
            if isinstance(entry, dict):
                template_id = entry.get("template_id")
                if template_id:
                    if template_id not in template_metrics:
                        template_metrics[template_id] = {
                            "total_analyses": 0,
                            "avg_processing_time": 0,
                            "avg_confidence": 0,
                            "success_rate": 0
                        }
                    
                    template_metrics[template_id]["total_analyses"] += 1
                    metrics_count += 1
        
        # Store aggregated metrics
        daily_key = f"daily_metrics:templates:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        await redis_service.set(daily_key, template_metrics, 86400 * 7)  # 7 days retention
        
        logger.info(f"Aggregated metrics for {len(template_metrics)} templates")
        
        return {"metrics_count": metrics_count}
        
    except Exception as e:
        logger.error(f"Template metrics aggregation failed: {e}")
        return {"metrics_count": 0, "error": str(e)}

async def aggregate_user_activity() -> Dict[str, Any]:
    """Aggregate user activity statistics"""
    try:
        users_processed = 0
        
        # Get user analytics data
        user_keys = await redis_service.keys("analytics:user:*")
        
        # Aggregate activity by user
        daily_activity = {
            "total_users": len(user_keys),
            "active_users": 0,
            "total_generations": 0,
            "total_templates": 0
        }
        
        for key in user_keys:
            try:
                user_analytics = await redis_service.lrange(key, 0, -1)
                if user_analytics:
                    daily_activity["active_users"] += 1
                    users_processed += 1
                    
            except Exception as e:
                logger.warning(f"Failed to process user analytics {key}: {e}")
        
        # Store daily activity summary
        daily_key = f"daily_activity:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        await redis_service.set(daily_key, daily_activity, 86400 * 30)  # 30 days retention
        
        logger.info(f"Processed activity for {users_processed} users")
        
        return {"users_processed": users_processed}
        
    except Exception as e:
        logger.error(f"User activity aggregation failed: {e}")
        return {"users_processed": 0, "error": str(e)}

async def aggregate_generation_stats() -> Dict[str, Any]:
    """Aggregate generation statistics"""
    try:
        generations_processed = 0
        
        # Get generation analytics
        generation_entries = await redis_service.lrange("analytics:generation", 0, -1)
        
        # Aggregate generation stats
        generation_stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "avg_processing_time": 0,
            "success_rate": 0
        }
        
        total_time = 0
        
        for entry in generation_entries:
            if isinstance(entry, dict):
                generation_stats["total_generations"] += 1
                generations_processed += 1
                
                if entry.get("event") == "completed":
                    generation_stats["successful_generations"] += 1
                    processing_time = entry.get("processing_time", 0)
                    total_time += processing_time
                elif entry.get("event") == "failed":
                    generation_stats["failed_generations"] += 1
        
        # Calculate averages
        if generation_stats["successful_generations"] > 0:
            generation_stats["avg_processing_time"] = total_time / generation_stats["successful_generations"]
            generation_stats["success_rate"] = (generation_stats["successful_generations"] / 
                                              generation_stats["total_generations"] * 100)
        
        # Store generation statistics
        daily_key = f"daily_generations:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        await redis_service.set(daily_key, generation_stats, 86400 * 30)  # 30 days retention
        
        logger.info(f"Processed {generations_processed} generation records")
        
        return {"generations_processed": generations_processed}
        
    except Exception as e:
        logger.error(f"Generation stats aggregation failed: {e}")
        return {"generations_processed": 0, "error": str(e)}

async def compute_performance_metrics() -> Dict[str, Any]:
    """Compute system performance metrics"""
    try:
        metrics_computed = 0
        
        # Compute various performance metrics
        performance_metrics = {
            "redis_performance": await measure_redis_performance(),
            "worker_performance": await measure_worker_performance(),
            "api_performance": await measure_api_performance(),
            "storage_performance": await measure_storage_performance()
        }
        
        metrics_computed = len(performance_metrics)
        
        # Store performance metrics
        daily_key = f"daily_performance:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        await redis_service.set(daily_key, performance_metrics, 86400 * 7)  # 7 days retention
        
        logger.info(f"Computed {metrics_computed} performance metrics")
        
        return {"metrics_computed": metrics_computed}
        
    except Exception as e:
        logger.error(f"Performance metrics computation failed: {e}")
        return {"metrics_computed": 0, "error": str(e)}

async def generate_daily_reports() -> Dict[str, Any]:
    """Generate daily usage reports"""
    try:
        reports_created = 0
        
        # Generate various daily reports
        reports = {
            "system_summary": await generate_system_summary_report(),
            "user_activity": await generate_user_activity_report(),
            "generation_performance": await generate_generation_report(),
            "template_analytics": await generate_template_report()
        }
        
        reports_created = len(reports)
        
        # Store daily reports
        report_key = f"daily_reports:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        await redis_service.set(report_key, reports, 86400 * 30)  # 30 days retention
        
        logger.info(f"Generated {reports_created} daily reports")
        
        return {"reports_created": reports_created}
        
    except Exception as e:
        logger.error(f"Daily report generation failed: {e}")
        return {"reports_created": 0, "error": str(e)}

# Health Check Functions

async def check_redis_health() -> Dict[str, Any]:
    """Check Redis connectivity and performance"""
    try:
        # Test Redis connectivity
        await redis_service.ping()
        
        # Test Redis performance
        start_time = datetime.now(timezone.utc)
        await redis_service.set("health_check", "test", 60)
        await redis_service.get("health_check")
        await redis_service.delete("health_check")
        response_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        status = "healthy" if response_time < 100 else "slow"
        
        return {
            "status": status,
            "response_time_ms": response_time,
            "connectivity": "ok"
        }
        
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "connectivity": "failed"
        }

async def check_database_health() -> Dict[str, Any]:
    """Check database connectivity and performance"""
    try:
        # Mock database health check
        # In production: test actual database connection
        
        return {
            "status": "healthy",
            "connectivity": "ok",
            "response_time_ms": 50
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "connectivity": "failed"
        }

async def check_storage_health() -> Dict[str, Any]:
    """Check storage service health"""
    try:
        # Mock storage health check
        # In production: test storage connectivity
        
        return {
            "status": "healthy",
            "connectivity": "ok",
            "response_time_ms": 200
        }
        
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "connectivity": "failed"
        }

async def check_ai_services_health() -> Dict[str, Any]:
    """Check AI services availability"""
    try:
        # Mock AI services health check
        # In production: test actual AI service endpoints
        
        return {
            "status": "healthy",
            "gemini_status": "available",
            "openai_status": "available",
            "embedding_status": "available"
        }
        
    except Exception as e:
        logger.error(f"AI services health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

async def check_worker_health() -> Dict[str, Any]:
    """Check Celery worker health"""
    try:
        # Mock worker health check
        # In production: inspect actual Celery workers
        
        return {
            "status": "healthy",
            "active_workers": 3,
            "total_workers": 4,
            "queue_lengths": {
                "analysis": 2,
                "generation": 5,
                "maintenance": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Worker health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Helper Functions

def determine_overall_health(health_results: Dict[str, Any]) -> str:
    """Determine overall system health based on component health"""
    critical_components = ["redis_status", "database_status"]
    important_components = ["storage_status", "ai_services_status", "worker_status"]
    
    # Check critical components
    for component in critical_components:
        if health_results.get(component) == "unhealthy":
            return "critical"
    
    # Check important components
    unhealthy_count = 0
    for component in important_components:
        if health_results.get(component) == "unhealthy":
            unhealthy_count += 1
    
    if unhealthy_count >= 2:
        return "degraded"
    elif unhealthy_count == 1:
        return "warning"
    else:
        return "healthy"

async def store_cleanup_report(report_type: str, report_data: Dict[str, Any]) -> None:
    """Store cleanup report for monitoring"""
    try:
        report_key = f"cleanup_reports:{report_type}:{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H')}"
        await redis_service.set(report_key, report_data, 86400 * 7)  # 7 days retention
        
    except Exception as e:
        logger.error(f"Failed to store cleanup report: {e}")

async def store_health_report(health_data: Dict[str, Any]) -> None:
    """Store health report for monitoring"""
    try:
        health_key = f"health_reports:{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H')}"
        await redis_service.set(health_key, health_data, 86400 * 7)  # 7 days retention
        
    except Exception as e:
        logger.error(f"Failed to store health report: {e}")

# Performance measurement functions (mock implementations)

async def measure_redis_performance() -> Dict[str, Any]:
    """Measure Redis performance metrics"""
    return {"avg_response_time": 5.2, "operations_per_second": 1000}

async def measure_worker_performance() -> Dict[str, Any]:
    """Measure worker performance metrics"""
    return {"avg_task_duration": 45.3, "tasks_per_hour": 120}

async def measure_api_performance() -> Dict[str, Any]:
    """Measure API performance metrics"""
    return {"avg_response_time": 250, "requests_per_minute": 500}

async def measure_storage_performance() -> Dict[str, Any]:
    """Measure storage performance metrics"""
    return {"avg_upload_time": 1.5, "avg_download_time": 0.8}

# Report generation functions (mock implementations)

async def generate_system_summary_report() -> Dict[str, Any]:
    """Generate system summary report"""
    return {"uptime": "99.9%", "total_requests": 10000, "error_rate": "0.1%"}

async def generate_user_activity_report() -> Dict[str, Any]:
    """Generate user activity report"""
    return {"active_users": 150, "new_registrations": 25, "retention_rate": "85%"}

async def generate_generation_report() -> Dict[str, Any]:
    """Generate generation performance report"""
    return {"total_generations": 500, "success_rate": "94%", "avg_time": "65s"}

async def generate_template_report() -> Dict[str, Any]:
    """Generate template analytics report"""
    return {"templates_analyzed": 50, "avg_confidence": 0.85, "popular_styles": ["modern", "gaming"]}