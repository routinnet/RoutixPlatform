"""
Test script for Redis and Celery functionality
"""
import asyncio
import time
from datetime import datetime
from app.services.redis_service import redis_service
from app.workers.celery_app import celery_app
from app.workers.test_tasks import (
    test_basic_task,
    test_async_task,
    health_check_task,
    test_error_handling
)

async def test_redis_connection():
    """Test Redis connection and basic operations"""
    print("🔍 Testing Redis Connection...")
    
    try:
        # Test ping
        ping_result = await redis_service.ping()
        print(f"✅ Redis ping: {ping_result}")
        
        # Test basic operations
        test_key = "test:redis:connection"
        test_value = {"message": "Hello Redis!", "timestamp": datetime.utcnow().isoformat()}
        
        # Set value
        set_result = await redis_service.set(test_key, test_value, 60)
        print(f"✅ Redis set: {set_result}")
        
        # Get value
        get_result = await redis_service.get(test_key)
        print(f"✅ Redis get: {get_result}")
        
        # Check exists
        exists_result = await redis_service.exists(test_key)
        print(f"✅ Redis exists: {exists_result}")
        
        # Delete value
        delete_result = await redis_service.delete(test_key)
        print(f"✅ Redis delete: {delete_result}")
        
        # Test hash operations
        hash_name = "test:hash"
        await redis_service.hset(hash_name, "field1", "value1")
        await redis_service.hset(hash_name, "field2", {"nested": "value"})
        
        hash_result = await redis_service.hgetall(hash_name)
        print(f"✅ Redis hash operations: {hash_result}")
        
        # Cleanup
        await redis_service.delete(hash_name)
        
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

def test_celery_connection():
    """Test Celery connection and basic task execution"""
    print("\n🔍 Testing Celery Connection...")
    
    try:
        # Test Celery inspect
        inspect = celery_app.control.inspect()
        
        # Check active workers
        active_workers = inspect.active()
        print(f"✅ Active Celery workers: {list(active_workers.keys()) if active_workers else 'None'}")
        
        # Check registered tasks
        registered_tasks = inspect.registered()
        if registered_tasks:
            for worker, tasks in registered_tasks.items():
                print(f"✅ Worker {worker} has {len(tasks)} registered tasks")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery connection test failed: {e}")
        return False

def test_celery_tasks():
    """Test Celery task execution"""
    print("\n🔍 Testing Celery Task Execution...")
    
    try:
        # Test basic task
        print("Testing basic task...")
        basic_task_result = test_basic_task.delay("Test message from script")
        print(f"✅ Basic task queued: {basic_task_result.id}")
        
        # Wait for result (with timeout)
        try:
            result = basic_task_result.get(timeout=30)
            print(f"✅ Basic task result: {result['status']}")
        except Exception as e:
            print(f"⚠️  Basic task timeout or error: {e}")
        
        # Test async task
        print("\nTesting async task...")
        async_task_data = {
            "test_id": "async_test_001",
            "parameters": {"param1": "value1", "param2": 42}
        }
        async_task_result = test_async_task.delay(async_task_data)
        print(f"✅ Async task queued: {async_task_result.id}")
        
        # Monitor progress
        print("Monitoring task progress...")
        for i in range(15):  # Check for up to 15 seconds
            if async_task_result.ready():
                result = async_task_result.get()
                print(f"✅ Async task completed: {result['status']}")
                break
            else:
                # Check task state
                if hasattr(async_task_result, 'state') and async_task_result.state == 'PROGRESS':
                    info = async_task_result.info
                    if info:
                        print(f"📊 Progress: {info.get('progress', 0)}% - {info.get('message', 'Processing...')}")
                time.sleep(1)
        
        # Test health check task
        print("\nTesting health check task...")
        health_task_result = health_check_task.delay()
        print(f"✅ Health check task queued: {health_task_result.id}")
        
        try:
            health_result = health_task_result.get(timeout=10)
            print(f"✅ Health check result: {health_result.get('celery_worker', 'unknown')}")
        except Exception as e:
            print(f"⚠️  Health check timeout or error: {e}")
        
        # Test error handling
        print("\nTesting error handling...")
        error_task_result = test_error_handling.delay(should_fail=False)
        print(f"✅ Error handling task queued: {error_task_result.id}")
        
        try:
            error_result = error_task_result.get(timeout=10)
            print(f"✅ Error handling result: {error_result['status']}")
        except Exception as e:
            print(f"⚠️  Error handling test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery task test failed: {e}")
        return False

async def test_redis_celery_integration():
    """Test Redis and Celery integration"""
    print("\n🔍 Testing Redis-Celery Integration...")
    
    try:
        # Test caching task results
        task_id = f"integration_test_{int(time.time())}"
        
        # Cache some data
        cache_key = f"task:result:{task_id}"
        cache_data = {
            "task_id": task_id,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        }
        
        cache_result = await redis_service.set(cache_key, cache_data, 300)
        print(f"✅ Cached task data: {cache_result}")
        
        # Retrieve cached data
        retrieved_data = await redis_service.get(cache_key)
        print(f"✅ Retrieved cached data: {retrieved_data['status']}")
        
        # Test pub/sub (basic publish)
        channel = "test:notifications"
        message = {
            "type": "test_message",
            "content": "Integration test message",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        publish_result = await redis_service.publish(channel, message)
        print(f"✅ Published message to channel: {publish_result} subscribers")
        
        # Test rate limiting
        rate_limit_key = "test:rate_limit"
        rate_limit_result = await redis_service.check_rate_limit(rate_limit_key, 10, 60)
        print(f"✅ Rate limit check: {rate_limit_result['allowed']} ({rate_limit_result['count']}/{rate_limit_result['limit']})")
        
        # Cleanup
        await redis_service.delete(cache_key)
        
        return True
        
    except Exception as e:
        print(f"❌ Redis-Celery integration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Redis & Celery Test Suite")
    print("=" * 50)
    
    # Test Redis
    redis_success = await test_redis_connection()
    
    # Test Celery
    celery_success = test_celery_connection()
    
    # Test Celery tasks (only if workers are available)
    if celery_success:
        task_success = test_celery_tasks()
    else:
        print("⚠️  Skipping task tests - no active workers")
        task_success = False
    
    # Test integration
    integration_success = await test_redis_celery_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Redis Connection: {'✅ PASS' if redis_success else '❌ FAIL'}")
    print(f"Celery Connection: {'✅ PASS' if celery_success else '❌ FAIL'}")
    print(f"Task Execution: {'✅ PASS' if task_success else '❌ FAIL'}")
    print(f"Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    overall_success = redis_success and celery_success and integration_success
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if not overall_success:
        print("\n💡 Troubleshooting Tips:")
        if not redis_success:
            print("- Check Redis server is running: redis-server")
            print("- Verify Redis URL in environment variables")
        if not celery_success:
            print("- Start Celery worker: celery -A app.workers.celery_app worker --loglevel=info")
            print("- Check Redis broker connection")
        if not task_success:
            print("- Ensure Celery workers are running and connected")
            print("- Check task routing and queue configuration")

if __name__ == "__main__":
    asyncio.run(main())