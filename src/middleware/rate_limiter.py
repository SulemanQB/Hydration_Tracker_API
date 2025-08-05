import time
from typing import Dict, Tuple, Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from config.settings import settings
import logging

logger = logging.getLogger("hydration_tracker.middleware")

class RateLimiter(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent API abuse"""
    
    def __init__(
        self, 
        app: ASGIApp, 
        requests_per_minute: int = settings.RATE_LIMIT_PER_MINUTE,
        exclude_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.exclude_paths = exclude_paths or ["/docs", "/openapi.json", "/redoc", "/app"]
        self.request_counts: Dict[str, Tuple[int, float]] = {}
        
        logger.info(f"Rate limiter initialized: {requests_per_minute} requests per minute")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for excluded paths
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if rate limit is enabled
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
            
        # Clean up old request counts
        self._cleanup_old_requests()
        
        # Check rate limit
        if not self._is_rate_limited(client_ip):
            # Proceed with request
            return await call_next(request)
        else:
            # Rate limited
            logger.warning(f"Rate limit exceeded for client: {client_ip}")
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=429,
                headers={"Retry-After": "60"}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request headers or direct connection"""
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # If behind a proxy, get the real client IP
            client_ip = x_forwarded_for.split(",")[0].strip()
        else:
            # Direct connection
            client_ip = request.client.host if request.client else "unknown"
        return client_ip
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if the client exceeds the rate limit"""
        current_time = time.time()
        
        if client_ip not in self.request_counts:
            # First request from this client
            self.request_counts[client_ip] = (1, current_time)
            return False
        
        count, timestamp = self.request_counts[client_ip]
        
        # If the window has expired, reset the counter
        if current_time - timestamp >= 60:
            self.request_counts[client_ip] = (1, current_time)
            return False
            
        # Check if client exceeded the limit
        if count >= self.requests_per_minute:
            return True
            
        # Increment the counter
        self.request_counts[client_ip] = (count + 1, timestamp)
        return False
    
    def _cleanup_old_requests(self) -> None:
        """Remove entries older than 2 minutes to prevent memory leaks"""
        current_time = time.time()
        keys_to_delete = []
        
        for client_ip, (count, timestamp) in self.request_counts.items():
            if current_time - timestamp >= 120:  # 2 minutes
                keys_to_delete.append(client_ip)
                
        for client_ip in keys_to_delete:
            del self.request_counts[client_ip]
