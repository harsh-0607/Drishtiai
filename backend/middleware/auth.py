from __future__ import annotations

import asyncio
import logging
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.services.firebase_auth import verify_bearer_token

logger = logging.getLogger(__name__)


class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    """Attach Firebase user info to request.state.user when token is valid.

    This middleware is permissive by default. Individual routers can enforce auth.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        auth_header = request.headers.get("authorization")
        try:
            user = await asyncio.to_thread(verify_bearer_token, auth_header)
        except Exception:
            user = None

        request.state.user = user
        return await call_next(request)
