from __future__ import annotations

import os
from typing import Optional

import redis.asyncio as redis


def get_redis() -> Optional[redis.Redis]:
    """Return an async Redis client if REDIS_URL is set (or default local)."""

    url = os.getenv("REDIS_URL")
    if not url:
        # allow running without redis
        return None
    return redis.from_url(url, decode_responses=True)
