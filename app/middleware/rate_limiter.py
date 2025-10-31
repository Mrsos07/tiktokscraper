"""
Rate limiting middleware for API protection
"""
import time
from collections import defaultdict, deque
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.logging import log


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm
    """
    
    def __init__(self, app, requests_per_minute: int = None, burst: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        self.burst = burst or settings.RATE_LIMIT_BURST
        
        # Store request timestamps per IP
        self.request_times = defaultdict(deque)
        
        # Cleanup interval (seconds)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        
        log.info(f"Rate limiter initialized: {self.requests_per_minute} req/min, burst: {self.burst}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and apply rate limiting
        """
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        current_time = time.time()
        
        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time
        
        # Get request times for this IP
        times = self.request_times[client_ip]
        
        # Remove requests older than 1 minute
        cutoff_time = current_time - 60
        while times and times[0] < cutoff_time:
            times.popleft()
        
        # Check if rate limit exceeded
        if len(times) >= self.requests_per_minute:
            log.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Too many requests",
                    "message": f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute allowed.",
                    "retry_after": 60 - (current_time - times[0])
                }
            )
        
        # Check burst limit (requests in last 10 seconds)
        burst_cutoff = current_time - 10
        burst_count = sum(1 for t in times if t > burst_cutoff)
        
        if burst_count >= self.burst:
            log.warning(f"Burst limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Too many requests",
                    "message": f"Burst limit exceeded. Maximum {self.burst} requests per 10 seconds allowed.",
                    "retry_after": 10
                }
            )
        
        # Add current request time
        times.append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(self.requests_per_minute - len(times))
        response.headers["X-RateLimit-Reset"] = str(int(times[0] + 60)) if times else str(int(current_time + 60))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request
        Handles proxies and load balancers
        """
        # Check X-Forwarded-For header (for proxies/load balancers)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get first IP in the chain
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _cleanup_old_entries(self, current_time: float):
        """
        Remove old entries to prevent memory leaks
        """
        cutoff_time = current_time - 300  # 5 minutes
        ips_to_remove = []
        
        for ip, times in self.request_times.items():
            # Remove old timestamps
            while times and times[0] < cutoff_time:
                times.popleft()
            
            # If no recent requests, mark for removal
            if not times:
                ips_to_remove.append(ip)
        
        # Remove empty entries
        for ip in ips_to_remove:
            del self.request_times[ip]
        
        if ips_to_remove:
            log.debug(f"Cleaned up {len(ips_to_remove)} inactive IPs from rate limiter")
