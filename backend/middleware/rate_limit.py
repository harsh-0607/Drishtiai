from __future__ import annotations

import asyncio
import time
from typing import Callable, Dict

from aiolimiter import AsyncLimiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple IP-based rate limiter.

    Defaults: 60 req/min per IP.

    Notes:
    - Uses an in-memory map of limiters per client IP.
    - Not suitable for multi-worker deployments unless you use a shared store.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self._requests_per_minute = requests_per_minute
        self._limiters: Dict[str, AsyncLimiter] = {}
        self._lock = asyncio.Lock()

    async def _get_limiter(self, ip: str) -> AsyncLimiter:
        async with self._lock:
            limiter = self._limiters.get(ip)
            if limiter is None:
                limiter = AsyncLimiter(max_rate=self._requests_per_minute, time_period=60)
                self._limiters[ip] = limiter
            return limiter

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        # Best-effort client IP; fall back to "unknown".
        ip = request.client.host if request.client else "unknown"

        limiter = await self._get_limiter(ip)

        try:
            # Avoid hanging forever if limiter is saturated.
            async with asyncio.timeout(2.0):
                async with limiter:
                    return await call_next(request)
        except TimeoutError:
            return JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": "1"},
            )
