import time
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from typing import Callable, Dict, Tuple
import re
from starlette.middleware.base import BaseHTTPMiddleware

from api.config import settings
from api.db.session import get_redis, redis_pool
from redis import asyncio as aioredis

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for certain paths
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") or request.url.path == "/health":
            return await call_next(request)

        # Get rate limit based on the path
        rate_limit, window = self._get_rate_limit_for_path(request.url.path)
        
        # Get publisher ID from request
        publisher_id = request.headers.get("X-Publisher-ID", None)
        if not publisher_id:
            publisher_id = "anonymous"
            
        # Create a rate limit key
        rate_limit_key = f"rate_limit:{publisher_id}:{request.url.path}"
        
        # Check if rate limit is exceeded
        is_rate_limited, remaining, reset_time = await self._check_rate_limit(
            rate_limit_key, rate_limit, window
        )
        
        if is_rate_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "rate_limit_exceeded",
                        "message": f"Rate limit exceeded. Try again in {reset_time} seconds.",
                        "details": {
                            "limit": rate_limit,
                            "window_seconds": window,
                            "reset_at": reset_time,
                        },
                    }
                },
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to the response
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def _get_rate_limit_for_path(self, path: str) -> Tuple[int, int]:
        """
        Determine the rate limit based on the request path.
        Returns (rate_limit, window_in_seconds)
        """
        # Convert rate limit strings to (limit, window) tuples
        def parse_rate_limit(rate_limit_str):
            limit, period = rate_limit_str.split("/")
            limit = int(limit)
            if period == "second":
                window = 1
            elif period == "minute":
                window = 60
            elif period == "hour":
                window = 3600
            else:
                window = 86400  # Default to daily
            return limit, window
        
        # Task-specific rate limits
        if re.match(r"^/v1/tasks/next", path):
            return parse_rate_limit(settings.RATE_LIMIT_TASKS)
        elif re.match(r"^/v1/tasks/.+/submit", path):
            return parse_rate_limit(settings.RATE_LIMIT_TASKS)
        elif re.match(r"^/v1/tasks/batch", path):
            return parse_rate_limit(settings.RATE_LIMIT_TASKS_BATCH)
        elif re.match(r"^/v1/users/sessions", path):
            return parse_rate_limit(settings.RATE_LIMIT_USERS_SESSIONS)
        
        # Default rate limit
        return parse_rate_limit(settings.RATE_LIMIT_DEFAULT)
    
    async def _check_rate_limit(
        self, key: str, limit: int, window: int
    ) -> Tuple[bool, int, int]:
        """
        Check if the request exceeds the rate limit.
        Returns (is_rate_limited, remaining_requests, reset_time)
        """
        if redis_pool is None:
            # If Redis is not available, allow the request
            return False, limit, window
        
        async with aioredis.Redis(connection_pool=redis_pool) as redis:
            # Get current timestamp
            current = int(time.time())
            # Window start time
            window_start = current - window
            
            # Create a pipeline to execute commands atomically
            pipeline = redis.pipeline()
            
            # Remove requests older than the window
            pipeline.zremrangebyscore(key, 0, window_start)
            # Count requests in the current window
            pipeline.zcard(key)
            # Add the current request
            pipeline.zadd(key, {str(current): current})
            # Set expiry on the key to clean up
            pipeline.expire(key, window)
            
            # Execute the pipeline
            results = await pipeline.execute()
            request_count = results[1]
            
            # Check if rate limit is exceeded
            is_rate_limited = request_count >= limit
            remaining = max(0, limit - request_count - 1)
            reset_time = window - (current % window) if window > 60 else window
            
            return is_rate_limited, remaining, reset_time