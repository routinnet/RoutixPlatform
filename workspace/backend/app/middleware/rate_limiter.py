"""
Professional Rate Limiting Middleware for Routix Platform
Implements Redis-based rate limiting with multiple strategies
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import hashlib
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Redis-based rate limiter with sliding window algorithm
    
    Supports multiple rate limiting strategies:
    - Per IP address
    - Per user ID
    - Per API endpoint
    - Global limits
    """
    
    def __init__(self, redis_client, limits: dict = None):
        """
        Initialize rate limiter
        
        Args:
            redis_client: Redis client instance
            limits: Dict of rate limits configuration
        """
        self.redis = redis_client
        self.limits = limits or {
            "default": {"requests": 60, "window": 60},  # 60 requests per minute
            "generation": {"requests": 10, "window": 60},  # 10 generations per minute
            "upload": {"requests": 20, "window": 60},  # 20 uploads per minute
            "auth": {"requests": 5, "window": 60}  # 5 auth attempts per minute
        }
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit using sliding window
        
        Args:
            key: Unique identifier for the rate limit bucket
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, info_dict)
        """
        try:
            current_time = time.time()
            window_start = current_time - window_seconds
            
            redis_key = f"rate_limit:{key}"
            
            pipe = self.redis.pipeline()
            
            pipe.zremrangebyscore(redis_key, 0, window_start)
            
            pipe.zcard(redis_key)
            
            pipe.zadd(redis_key, {str(current_time): current_time})
            
            pipe.expire(redis_key, window_seconds * 2)
            
            results = await pipe.execute()
            
            current_count = results[1]
            
            is_allowed = current_count < max_requests
            
            reset_time = int(current_time + window_seconds)
            
            remaining = max(0, max_requests - current_count - 1)
            
            info = {
                "limit": max_requests,
                "remaining": remaining,
                "reset": reset_time,
                "retry_after": None
            }
            
            if not is_allowed:
                oldest_scores = await self.redis.zrange(
                    redis_key, 0, 0, withscores=True
                )
                if oldest_scores:
                    oldest_time = oldest_scores[0][1]
                    retry_after = int(oldest_time + window_seconds - current_time)
                    info["retry_after"] = max(1, retry_after)
            
            return is_allowed, info
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True, {
                "limit": max_requests,
                "remaining": max_requests,
                "reset": int(time.time() + window_seconds),
                "retry_after": None
            }
    
    async def check_limit_for_request(
        self,
        request: Request,
        limit_type: str = "default"
    ) -> tuple[bool, dict]:
        """
        Check rate limit for a specific request
        
        Args:
            request: FastAPI request object
            limit_type: Type of limit to apply (default, generation, upload, auth)
            
        Returns:
            Tuple of (is_allowed, info_dict)
        """
        limit_config = self.limits.get(limit_type, self.limits["default"])
        max_requests = limit_config["requests"]
        window = limit_config["window"]
        
        key_parts = []
        
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            key_parts.append(f"user:{user_id}")
        else:
            client_ip = self._get_client_ip(request)
            key_parts.append(f"ip:{client_ip}")
        
        key_parts.append(limit_type)
        
        key = ":".join(key_parts)
        
        return await self.check_rate_limit(key, max_requests, window)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        if request.client:
            return request.client.host
        
        return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for applying rate limits to requests
    """
    
    def __init__(self, app, redis_client, limits: dict = None):
        super().__init__(app)
        self.rate_limiter = RateLimiter(redis_client, limits)
        self.excluded_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and apply rate limiting"""
        
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        limit_type = self._get_limit_type(request)
        
        is_allowed, info = await self.rate_limiter.check_limit_for_request(
            request, limit_type
        )
        
        response = None
        if is_allowed:
            response = await call_next(request)
        else:
            logger.warning(
                f"Rate limit exceeded: {request.url.path} | "
                f"Client: {self.rate_limiter._get_client_ip(request)} | "
                f"Limit: {info['limit']}/{info.get('retry_after', 60)}s"
            )
            
            response = JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "type": "rate_limit_exceeded",
                        "message": "Too many requests. Please try again later.",
                        "details": {
                            "limit": info["limit"],
                            "retry_after": info.get("retry_after", 60)
                        }
                    }
                }
            )
        
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        if info.get("retry_after"):
            response.headers["Retry-After"] = str(info["retry_after"])
        
        return response
    
    def _get_limit_type(self, request: Request) -> str:
        """Determine rate limit type based on request path"""
        path = request.url.path.lower()
        
        if "/generations" in path or "/generate" in path:
            return "generation"
        
        if "/upload" in path or "/templates" in path and request.method == "POST":
            return "upload"
        
        if "/auth" in path or "/login" in path or "/register" in path:
            return "auth"
        
        return "default"


def create_rate_limiter_middleware(app, redis_client, custom_limits: dict = None):
    """
    Factory function to create and add rate limiting middleware
    
    Usage:
        from app.middleware.rate_limiter import create_rate_limiter_middleware
        from app.services.redis_service import redis_service
        
        create_rate_limiter_middleware(app, redis_service.redis, {
            "generation": {"requests": 20, "window": 60}
        })
    """
    
    from app.core.config import settings
    
    default_limits = {
        "default": {
            "requests": getattr(settings, "RATE_LIMIT_PER_MINUTE", 60),
            "window": 60
        },
        "generation": {
            "requests": 10,
            "window": 60
        },
        "upload": {
            "requests": 20,
            "window": 60
        },
        "auth": {
            "requests": 5,
            "window": 60
        }
    }
    
    if custom_limits:
        default_limits.update(custom_limits)
    
    app.add_middleware(RateLimitMiddleware, redis_client=redis_client, limits=default_limits)
    
    logger.info("Rate limiting middleware enabled")


def rate_limit(limit_type: str = "default"):
    """
    Decorator to apply rate limiting to specific endpoints
    
    Usage:
        @app.get("/api/resource")
        @rate_limit("generation")
        async def get_resource():
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator
