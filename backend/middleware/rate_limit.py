from __future__ import annotations

import asyncio
import time
from typing import Callable

from aiolimiter import AsyncLimiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple IP-based rate limiter.

    Defaults: 60 req/min per IP.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self._limiter = AsyncLimiter(max_rate=requests_per_minute, time_period=60)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        async with self._limiter:
            return await call_next(request)
