"""
Redis service for caching and pub/sub operations
"""
import json
import redis
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from app.core.config import settings

class RedisService:
    """Redis service for caching, sessions, and pub/sub"""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        self.default_ttl = 3600  # 1 hour
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            print(f"Redis ping failed: {e}")
            return False
    
    # Cache operations
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            print(f"Redis set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Redis delete failed for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Redis exists check failed for key {key}: {e}")
            return False
    
    # Hash operations
    async def hget(self, name: str, key: str) -> Optional[Any]:
        """Get field from hash"""
        try:
            value = self.redis_client.hget(name, key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis hget failed for {name}.{key}: {e}")
            return None
    
    async def hset(self, name: str, key: str, value: Any) -> bool:
        """Set field in hash"""
        try:
            serialized_value = json.dumps(value, default=str)
            return bool(self.redis_client.hset(name, key, serialized_value))
        except Exception as e:
            print(f"Redis hset failed for {name}.{key}: {e}")
            return False
    
    async def hgetall(self, name: str) -> Dict[str, Any]:
        """Get all fields from hash"""
        try:
            hash_data = self.redis_client.hgetall(name)
            return {k: json.loads(v) for k, v in hash_data.items()}
        except Exception as e:
            print(f"Redis hgetall failed for {name}: {e}")
            return {}
    
    # List operations
    async def lpush(self, name: str, *values: Any) -> int:
        """Push values to left of list"""
        try:
            serialized_values = [json.dumps(v, default=str) for v in values]
            return self.redis_client.lpush(name, *serialized_values)
        except Exception as e:
            print(f"Redis lpush failed for {name}: {e}")
            return 0
    
    async def rpop(self, name: str) -> Optional[Any]:
        """Pop value from right of list"""
        try:
            value = self.redis_client.rpop(name)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis rpop failed for {name}: {e}")
            return None
    
    async def llen(self, name: str) -> int:
        """Get length of list"""
        try:
            return self.redis_client.llen(name)
        except Exception as e:
            print(f"Redis llen failed for {name}: {e}")
            return 0
    
    # Pub/Sub operations
    async def publish(self, channel: str, message: Dict[str, Any]) -> int:
        """Publish message to channel"""
        try:
            serialized_message = json.dumps(message, default=str)
            return self.redis_client.publish(channel, serialized_message)
        except Exception as e:
            print(f"Redis publish failed for channel {channel}: {e}")
            return 0
    
    # Session management
    async def create_session(self, session_id: str, user_data: Dict[str, Any], ttl: int = 86400) -> bool:
        """Create user session (24 hours default)"""
        session_key = f"session:{session_id}"
        return await self.set(session_key, user_data, ttl)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data"""
        session_key = f"session:{session_id}"
        return await self.get(session_key)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete user session"""
        session_key = f"session:{session_id}"
        return await self.delete(session_key)
    
    # Rate limiting
    async def check_rate_limit(self, key: str, limit: int, window: int) -> Dict[str, Any]:
        """Check rate limit for key (sliding window)"""
        try:
            current_time = datetime.utcnow()
            window_start = current_time - timedelta(seconds=window)
            
            # Use sorted set for sliding window
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start.timestamp())
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time.timestamp()): current_time.timestamp()})
            pipe.expire(key, window)
            
            results = pipe.execute()
            current_count = results[1]
            
            return {
                'allowed': current_count < limit,
                'count': current_count,
                'limit': limit,
                'reset_time': (current_time + timedelta(seconds=window)).isoformat()
            }
        except Exception as e:
            print(f"Rate limit check failed for {key}: {e}")
            return {'allowed': True, 'count': 0, 'limit': limit}
    
    # Cache specific methods for Routix
    async def cache_user_credits(self, user_id: str, credits: int, ttl: int = 300) -> bool:
        """Cache user credits (5 minutes default)"""
        key = f"user:credits:{user_id}"
        return await self.set(key, credits, ttl)
    
    async def get_user_credits(self, user_id: str) -> Optional[int]:
        """Get cached user credits"""
        key = f"user:credits:{user_id}"
        return await self.get(key)
    
    async def cache_template_analysis(self, template_id: str, analysis: Dict[str, Any], ttl: int = 86400) -> bool:
        """Cache template analysis (24 hours default)"""
        key = f"template:analysis:{template_id}"
        return await self.set(key, analysis, ttl)
    
    async def get_template_analysis(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get cached template analysis"""
        key = f"template:analysis:{template_id}"
        return await self.get(key)
    
    async def cache_search_results(self, query_hash: str, results: List[Dict], ttl: int = 300) -> bool:
        """Cache search results (5 minutes default)"""
        key = f"search:results:{query_hash}"
        return await self.set(key, results, ttl)
    
    async def get_search_results(self, query_hash: str) -> Optional[List[Dict]]:
        """Get cached search results"""
        key = f"search:results:{query_hash}"
        return await self.get(key)

# Global Redis service instance
redis_service = RedisService()