import time
import uuid
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import structlog
from typing import Callable, Dict, Any

from api.config import settings

# Configure structlog
logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""
    
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.log_level = getattr(logging, settings.LOG_LEVEL)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Extract request info
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent", "")
        publisher_id = request.headers.get("X-Publisher-ID", "unknown")
        
        # Log request start
        start_time = time.time()
        log_data = {
            "event": "request_start",
            "request_id": request_id,
            "method": method,
            "path": path,
            "query_params": query_params,
            "client_host": client_host,
            "user_agent": user_agent,
            "publisher_id": publisher_id,
        }
        
        if settings.DEBUG:
            # In debug mode, also log headers (excluding sensitive ones)
            headers = dict(request.headers)
            if "Authorization" in headers:
                headers["Authorization"] = "[REDACTED]"
            if "Cookie" in headers:
                headers["Cookie"] = "[REDACTED]"
            log_data["headers"] = headers
        
        # Skip logging for health check endpoints to avoid cluttering logs
        if not path.endswith("/health"):
            logger.info("API request received", **log_data)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate request processing time
            process_time = time.time() - start_time
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log response data
            log_data.update({
                "event": "request_end",
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
            })
            
            # Skip logging for health check endpoints
            if not path.endswith("/health"):
                log_method = logger.info if response.status_code < 400 else logger.error
                log_method("API request completed", **log_data)
            
            return response
            
        except Exception as e:
            # Log exception
            process_time = time.time() - start_time
            
            log_data.update({
                "event": "request_error",
                "error": str(e),
                "error_type": type(e).__name__,
                "process_time_ms": round(process_time * 1000, 2),
            })
            
            logger.exception("API request failed", **log_data)
            raise